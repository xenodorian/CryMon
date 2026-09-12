"""Minimal two-pass 65816 assembler targeting SNES LoROM."""

from __future__ import annotations


class AsmError(RuntimeError):
    pass


class Asm:
    ROM_SIZE = 256 * 1024  # 8 LoROM banks

    def __init__(self):
        self.rom = bytearray(self.ROM_SIZE)
        self.bank = 0
        self.pc = 0x8000
        self.labels: dict[str, tuple[int, int]] = {}
        self.pass_n = 1
        self.m8 = True
        self.x8 = True
        self.listing: list[str] = []
        self._org_pc = 0x8000
        self._org_bank = 0

    def off(self) -> int:
        return (self.bank & 0x7F) * 0x8000 + (self.pc & 0x7FFF)

    def org(self, bank: int, addr: int = 0x8000):
        if addr < 0x8000 or addr > 0xFFFF:
            raise AsmError(f"LoROM org addr {addr:04X} not in $8000-$FFFF")
        self.bank = bank
        self.pc = addr
        self._org_bank = bank
        self._org_pc = addr

    def label(self, name: str):
        here = (self.bank, self.pc)
        if self.pass_n == 1:
            if name in self.labels and self.labels[name] != here:
                raise AsmError(f"label {name} redefined")
            self.labels[name] = here
        else:
            if self.labels.get(name) != here:
                raise AsmError(f"label {name} moved {self.labels.get(name)} -> {here}")

    def emit(self, *bs: int):
        off = self.off()
        for i, b in enumerate(bs):
            if off + i >= self.ROM_SIZE:
                raise AsmError(f"ROM overflow at {self.bank:02X}:{self.pc:04X}")
            if self.pass_n == 2:
                self.rom[off + i] = b & 0xFF
        self.pc += len(bs)
        if self.pc > 0x10000:
            raise AsmError("bank overflow")

    def db(self, *vals):
        for v in vals:
            if isinstance(v, (bytes, bytearray)):
                self.emit(*v)
            elif isinstance(v, str):
                self.emit(*v.encode("ascii"))
            else:
                self.emit(int(v) & 0xFF)

    def dw(self, *vals):
        for v in vals:
            n = self._num(v, 2)
            self.emit(n & 0xFF, (n >> 8) & 0xFF)

    def dl(self, *vals):
        for v in vals:
            n = self._num(v, 3)
            self.emit(n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF)

    def ascii(self, s: str):
        self.emit(*s.encode("ascii"))

    def asciiz(self, s: str):
        self.emit(*s.encode("ascii"), 0)

    def align(self, n: int):
        while self.pc % n:
            self.emit(0x00)

    def _num(self, v, nbytes: int) -> int:
        if isinstance(v, tuple):
            base = self._num(v[0], nbytes)
            return (base + int(v[1])) & ((1 << (8 * nbytes)) - 1)
        if isinstance(v, str):
            if self.pass_n == 1:
                return 0
            if v not in self.labels:
                raise AsmError(f"undefined label {v}")
            b, a = self.labels[v]
            if nbytes == 1:
                return a & 0xFF
            if nbytes == 2:
                return a & 0xFFFF
            return ((b & 0xFF) << 16) | (a & 0xFFFF)
        return int(v)

    def _rel8(self, name: str) -> int:
        if self.pass_n == 1:
            return 0
        if name not in self.labels:
            raise AsmError(f"undefined label {name}")
        b, a = self.labels[name]
        if b != self.bank:
            raise AsmError(f"rel8 {name} crosses bank")
        rel = a - (self.pc + 1)
        if rel < -128 or rel > 127:
            raise AsmError(f"branch {name} out of range ({rel}) at {self.bank:02X}:{self.pc:04X}")
        return rel & 0xFF

    def _rel16(self, name: str) -> int:
        if self.pass_n == 1:
            return 0
        if name not in self.labels:
            raise AsmError(f"undefined label {name}")
        b, a = self.labels[name]
        if b != self.bank:
            raise AsmError(f"rel16 {name} crosses bank")
        # BRL is 3 bytes; displacement is from the following instruction.
        rel = a - (self.pc + 3)
        if rel < -32768 or rel > 32767:
            raise AsmError(f"brl {name} out of range")
        return rel & 0xFFFF

    def loc(self, name: str) -> tuple[int, int]:
        if name not in self.labels:
            if self.pass_n == 1:
                return (0, 0)
            raise AsmError(f"undefined label {name}")
        return self.labels[name]

    # flag helpers
    def sep(self, v: int):
        self.emit(0xE2, v & 0xFF)
        if v & 0x20:
            self.m8 = True
        if v & 0x10:
            self.x8 = True

    def rep(self, v: int):
        self.emit(0xC2, v & 0xFF)
        if v & 0x20:
            self.m8 = False
        if v & 0x10:
            self.x8 = False

    def a8(self):
        if not self.m8:
            self.sep(0x20)

    def a16(self):
        if self.m8:
            self.rep(0x20)

    def xy8(self):
        if not self.x8:
            self.sep(0x10)

    def xy16(self):
        if self.x8:
            self.rep(0x10)

    def a8xy16(self):
        # Always emit. Assembler sequential M/X is not runtime M/X;
        # a no-op here desyncs 8/16-bit immediates (ldx #$4000 becomes ldx #$00 / RTI).
        self.emit(0xE2, 0x20)  # sep #$20
        self.m8 = True
        self.emit(0xC2, 0x10)  # rep #$10
        self.x8 = False

    # implied
    def sei(self):
        self.emit(0x78)

    def cli(self):
        self.emit(0x58)

    def clc(self):
        self.emit(0x18)

    def sec(self):
        self.emit(0x38)

    def cld(self):
        self.emit(0xD8)

    def xce(self):
        self.emit(0xFB)

    def nop(self):
        self.emit(0xEA)

    def pha(self):
        self.emit(0x48)

    def pla(self):
        self.emit(0x68)

    def phx(self):
        self.emit(0xDA)

    def plx(self):
        self.emit(0xFA)

    def phy(self):
        self.emit(0x5A)

    def ply(self):
        self.emit(0x7A)

    def php(self):
        self.emit(0x08)

    def plp(self):
        self.emit(0x28)

    def phb(self):
        self.emit(0x8B)

    def plb(self):
        self.emit(0xAB)

    def phd(self):
        self.emit(0x0B)

    def pld(self):
        self.emit(0x2B)

    def phk(self):
        self.emit(0x4B)

    def rts(self):
        self.emit(0x60)

    def rtl(self):
        self.emit(0x6B)

    def rti(self):
        self.emit(0x40)

    def inx(self):
        self.emit(0xE8)

    def dex(self):
        self.emit(0xCA)

    def iny(self):
        self.emit(0xC8)

    def dey(self):
        self.emit(0x88)

    def tax(self):
        self.emit(0xAA)

    def txa(self):
        self.emit(0x8A)

    def tay(self):
        self.emit(0xA8)

    def tya(self):
        self.emit(0x98)

    def tsx(self):
        self.emit(0xBA)

    def txs(self):
        self.emit(0x9A)

    def txy(self):
        self.emit(0x9B)

    def tyx(self):
        self.emit(0xBB)

    def tcd(self):
        self.emit(0x5B)

    def tdc(self):
        self.emit(0x7B)

    def tcs(self):
        self.emit(0x1B)

    def tsc(self):
        self.emit(0x3B)

    def xba(self):
        self.emit(0xEB)

    def wai(self):
        self.emit(0xCB)

    def inca(self):
        self.emit(0x1A)

    def deca(self):
        self.emit(0x3A)

    def asl_a(self):
        self.emit(0x0A)

    def lsr_a(self):
        self.emit(0x4A)

    def rol_a(self):
        self.emit(0x2A)

    def ror_a(self):
        self.emit(0x6A)

    def _imm_size(self, which: str) -> int:
        if which == "a":
            return 1 if self.m8 else 2
        return 1 if self.x8 else 2

    def _imm(self, opcode: int, v, which: str):
        n = self._imm_size(which)
        val = self._num(v, n)
        if n == 1:
            self.emit(opcode, val & 0xFF)
        else:
            self.emit(opcode, val & 0xFF, (val >> 8) & 0xFF)

    def lda_imm(self, v):
        self._imm(0xA9, v, "a")

    def ldx_imm(self, v):
        self._imm(0xA2, v, "x")

    def ldy_imm(self, v):
        self._imm(0xA0, v, "x")

    def adc_imm(self, v):
        self._imm(0x69, v, "a")

    def sbc_imm(self, v):
        self._imm(0xE9, v, "a")

    def cmp_imm(self, v):
        self._imm(0xC9, v, "a")

    def cpx_imm(self, v):
        self._imm(0xE0, v, "x")

    def cpy_imm(self, v):
        self._imm(0xC0, v, "x")

    def and_imm(self, v):
        self._imm(0x29, v, "a")

    def ora_imm(self, v):
        self._imm(0x09, v, "a")

    def eor_imm(self, v):
        self._imm(0x49, v, "a")

    def bit_imm(self, v):
        self._imm(0x89, v, "a")

    def lda_zp(self, z):
        self.emit(0xA5, self._num(z, 1) & 0xFF)

    def lda_zpx(self, z):
        self.emit(0xB5, self._num(z, 1) & 0xFF)

    def lda_ind(self, z):
        self.emit(0xB2, self._num(z, 1) & 0xFF)

    def lda_indy(self, z):
        self.emit(0xB1, self._num(z, 1) & 0xFF)

    def lda_longind(self, z):
        self.emit(0xA7, self._num(z, 1) & 0xFF)

    def lda_longindy(self, z):
        self.emit(0xB7, self._num(z, 1) & 0xFF)

    def sta_longind(self, z):
        self.emit(0x87, self._num(z, 1) & 0xFF)

    def adc_absx(self, v):
        n = self._num(v, 2)
        self.emit(0x7D, n & 0xFF, (n >> 8) & 0xFF)

    def sbc_absx(self, v):
        n = self._num(v, 2)
        self.emit(0xFD, n & 0xFF, (n >> 8) & 0xFF)

    def lda_abs(self, v):
        n = self._num(v, 2)
        self.emit(0xAD, n & 0xFF, (n >> 8) & 0xFF)

    def lda_absx(self, v):
        n = self._num(v, 2)
        self.emit(0xBD, n & 0xFF, (n >> 8) & 0xFF)

    def lda_absy(self, v):
        n = self._num(v, 2)
        self.emit(0xB9, n & 0xFF, (n >> 8) & 0xFF)

    def lda_long(self, v):
        n = self._num(v, 3)
        self.emit(0xAF, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF)

    def lda_longx(self, v):
        n = self._num(v, 3)
        self.emit(0xBF, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF)

    def sta_zp(self, z):
        self.emit(0x85, self._num(z, 1) & 0xFF)

    def sta_zpx(self, z):
        self.emit(0x95, self._num(z, 1) & 0xFF)

    def sta_ind(self, z):
        self.emit(0x92, self._num(z, 1) & 0xFF)

    def sta_indy(self, z):
        self.emit(0x91, self._num(z, 1) & 0xFF)

    def sta_abs(self, v):
        n = self._num(v, 2)
        self.emit(0x8D, n & 0xFF, (n >> 8) & 0xFF)

    def split16(self, addr: int, val):
        """Write 16-bit val to addr/addr+1 as two 8-bit stores. Requires A8."""
        n = self._num(val, 2)
        self.emit(0xA9, n & 0xFF)
        self.emit(0x8D, addr & 0xFF, (addr >> 8) & 0xFF)
        self.emit(0xA9, (n >> 8) & 0xFF)
        self.emit(0x8D, (addr + 1) & 0xFF, ((addr + 1) >> 8) & 0xFF)

    def sta_absx(self, v):
        n = self._num(v, 2)
        self.emit(0x9D, n & 0xFF, (n >> 8) & 0xFF)

    def sta_absy(self, v):
        n = self._num(v, 2)
        self.emit(0x99, n & 0xFF, (n >> 8) & 0xFF)

    def sta_long(self, v):
        n = self._num(v, 3)
        self.emit(0x8F, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF)

    def sta_longx(self, v):
        n = self._num(v, 3)
        self.emit(0x9F, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF)

    def stx_zp(self, z):
        self.emit(0x86, self._num(z, 1) & 0xFF)

    def stx_abs(self, v):
        n = self._num(v, 2)
        self.emit(0x8E, n & 0xFF, (n >> 8) & 0xFF)

    def sty_zp(self, z):
        self.emit(0x84, self._num(z, 1) & 0xFF)

    def sty_abs(self, v):
        n = self._num(v, 2)
        self.emit(0x8C, n & 0xFF, (n >> 8) & 0xFF)

    def stz_zp(self, z):
        self.emit(0x64, self._num(z, 1) & 0xFF)

    def stz_zpx(self, z):
        self.emit(0x74, self._num(z, 1) & 0xFF)

    def stz_abs(self, v):
        n = self._num(v, 2)
        self.emit(0x9C, n & 0xFF, (n >> 8) & 0xFF)

    def stz_absx(self, v):
        n = self._num(v, 2)
        self.emit(0x9E, n & 0xFF, (n >> 8) & 0xFF)

    def ldx_zp(self, z):
        self.emit(0xA6, self._num(z, 1) & 0xFF)

    def ldx_abs(self, v):
        n = self._num(v, 2)
        self.emit(0xAE, n & 0xFF, (n >> 8) & 0xFF)

    def ldx_absy(self, v):
        n = self._num(v, 2)
        self.emit(0xBE, n & 0xFF, (n >> 8) & 0xFF)

    def ldy_zp(self, z):
        self.emit(0xA4, self._num(z, 1) & 0xFF)

    def ldy_abs(self, v):
        n = self._num(v, 2)
        self.emit(0xAC, n & 0xFF, (n >> 8) & 0xFF)

    def ldy_absx(self, v):
        n = self._num(v, 2)
        self.emit(0xBC, n & 0xFF, (n >> 8) & 0xFF)

    def adc_zp(self, z):
        self.emit(0x65, self._num(z, 1) & 0xFF)

    def adc_abs(self, v):
        n = self._num(v, 2)
        self.emit(0x6D, n & 0xFF, (n >> 8) & 0xFF)

    def sbc_zp(self, z):
        self.emit(0xE5, self._num(z, 1) & 0xFF)

    def sbc_abs(self, v):
        n = self._num(v, 2)
        self.emit(0xED, n & 0xFF, (n >> 8) & 0xFF)

    def cmp_zp(self, z):
        self.emit(0xC5, self._num(z, 1) & 0xFF)

    def cmp_abs(self, v):
        n = self._num(v, 2)
        self.emit(0xCD, n & 0xFF, (n >> 8) & 0xFF)

    def cmp_absx(self, v):
        n = self._num(v, 2)
        self.emit(0xDD, n & 0xFF, (n >> 8) & 0xFF)

    def cpx_zp(self, z):
        self.emit(0xE4, self._num(z, 1) & 0xFF)

    def cpy_zp(self, z):
        self.emit(0xC4, self._num(z, 1) & 0xFF)

    def and_zp(self, z):
        self.emit(0x25, self._num(z, 1) & 0xFF)

    def and_abs(self, v):
        n = self._num(v, 2)
        self.emit(0x2D, n & 0xFF, (n >> 8) & 0xFF)

    def ora_zp(self, z):
        self.emit(0x05, self._num(z, 1) & 0xFF)

    def ora_abs(self, v):
        n = self._num(v, 2)
        self.emit(0x0D, n & 0xFF, (n >> 8) & 0xFF)

    def eor_zp(self, z):
        self.emit(0x45, self._num(z, 1) & 0xFF)

    def bit_zp(self, z):
        self.emit(0x24, self._num(z, 1) & 0xFF)

    def bit_abs(self, v):
        n = self._num(v, 2)
        self.emit(0x2C, n & 0xFF, (n >> 8) & 0xFF)

    def inc_zp(self, z):
        self.emit(0xE6, self._num(z, 1) & 0xFF)

    def inc_abs(self, v):
        n = self._num(v, 2)
        self.emit(0xEE, n & 0xFF, (n >> 8) & 0xFF)

    def inc_absx(self, v):
        n = self._num(v, 2)
        self.emit(0xFE, n & 0xFF, (n >> 8) & 0xFF)

    def dec_zp(self, z):
        self.emit(0xC6, self._num(z, 1) & 0xFF)

    def dec_abs(self, v):
        n = self._num(v, 2)
        self.emit(0xCE, n & 0xFF, (n >> 8) & 0xFF)

    def dec_absx(self, v):
        n = self._num(v, 2)
        self.emit(0xDE, n & 0xFF, (n >> 8) & 0xFF)

    def asl_zp(self, z):
        self.emit(0x06, self._num(z, 1) & 0xFF)

    def lsr_zp(self, z):
        self.emit(0x46, self._num(z, 1) & 0xFF)

    def rol_zp(self, z):
        self.emit(0x26, self._num(z, 1) & 0xFF)

    def ror_zp(self, z):
        self.emit(0x66, self._num(z, 1) & 0xFF)

    def jmp(self, v):
        n = self._num(v, 2)
        self.emit(0x4C, n & 0xFF, (n >> 8) & 0xFF)

    def jsr(self, v):
        n = self._num(v, 2)
        self.emit(0x20, n & 0xFF, (n >> 8) & 0xFF)

    def jsl(self, v):
        n = self._num(v, 3)
        self.emit(0x22, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF)

    def jml(self, v):
        n = self._num(v, 3)
        self.emit(0x5C, n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF)

    def bra(self, name: str):
        # Unconditional JMP — BRL displacement was easy to get wrong and
        # a missed RTS fell into the next routine (oam_add → bg3_clear).
        self.jmp(name)

    def brl(self, name: str):
        r = self._rel16(name)
        self.emit(0x82, r & 0xFF, (r >> 8) & 0xFF)

    def beq(self, name: str):
        self.beq_far(name)

    def bne(self, name: str):
        self.bne_far(name)

    def bcc(self, name: str):
        self.bcc_far(name)

    def bcs(self, name: str):
        self.bcs_far(name)

    def bmi(self, name: str):
        self.bmi_far(name)

    def bpl(self, name: str):
        self.bpl_far(name)

    def bvc(self, name: str):
        self.emit(0x50, self._rel8(name))

    def bvs(self, name: str):
        self.emit(0x70, self._rel8(name))

    def beq_far(self, name: str):
        self.emit(0xD0, 0x03)  # bne +3
        self.jmp(name)

    def bne_far(self, name: str):
        self.emit(0xF0, 0x03)
        self.jmp(name)

    def bcc_far(self, name: str):
        self.emit(0xB0, 0x03)
        self.jmp(name)

    def bcs_far(self, name: str):
        self.emit(0x90, 0x03)
        self.jmp(name)

    def bpl_far(self, name: str):
        self.emit(0x30, 0x03)
        self.jmp(name)

    def bmi_far(self, name: str):
        self.emit(0x10, 0x03)
        self.jmp(name)

    def pea(self, v):
        n = self._num(v, 2)
        self.emit(0xF4, n & 0xFF, (n >> 8) & 0xFF)

    def assemble(self, fn):
        self.pass_n = 1
        self.rom = bytearray(self.ROM_SIZE)
        self.labels.clear()
        self.m8 = True
        self.x8 = True
        self.bank = 0
        self.pc = 0x8000
        fn(self)
        self.pass_n = 2
        self.m8 = True
        self.x8 = True
        self.bank = 0
        self.pc = 0x8000
        fn(self)
        return self.rom
