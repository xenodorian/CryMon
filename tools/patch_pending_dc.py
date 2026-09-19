#!/usr/bin/env python3
"""Wire Dreamcast PENDING dispatch for marshBog, marshReed, opal."""
from pathlib import Path

def patch_bake():
    path = Path("tools/bake_content.py")
    bake = path.read_text()
    if '"marshBog", "marshReed", "opal"' not in bake:
        if '"quarryDriller"]' in bake:
            bake = bake.replace(
                '"quarryDriller"]',
                '"quarryDriller", "marshBog", "marshReed", "opal"]',
                1,
            )
        else:
            raise SystemExit("kit_keys anchor not found")
    if "NPC_PENDING_MARSH_BOG" not in bake:
        bake = bake.replace(
            'lines.append("#define NPC_PENDING_QUARRY_DRILLER 12")',
            'lines.append("#define NPC_PENDING_QUARRY_DRILLER 12")\n'
            '    lines.append("#define NPC_PENDING_MARSH_BOG 9")\n'
            '    lines.append("#define NPC_PENDING_MARSH_REED 10")\n'
            '    lines.append("#define NPC_PENDING_OPAL 11")',
        )
    path.write_text(bake)
    print("bake_content.py ok")

def patch_main():
    path = Path("ports/dreamcast/src/main.c")
    main = path.read_text()
    if "TRAINER_WSOLDIER_OPAL" in main and "beat_marsh_bog" in main:
        print("main.c already patched")
        return

    main = main.replace(
        "#define TRAINER_WSOLDIER_QUARRY_DRILLER 15\n",
        "#define TRAINER_WSOLDIER_QUARRY_DRILLER 15\n"
        "#define TRAINER_WSOLDIER_OPAL 16\n"
        "#define TRAINER_WSOLDIER_MARSH_BOG 17\n"
        "#define TRAINER_WSOLDIER_MARSH_REED 18\n",
    )
    main = main.replace(
        "#define POST_WSOLDIER_QUARRY_DRILLER 23\n",
        "#define POST_WSOLDIER_QUARRY_DRILLER 23\n"
        "#define POST_WSOLDIER_OPAL 24\n"
        "#define POST_WSOLDIER_MARSH_BOG 25\n"
        "#define POST_WSOLDIER_MARSH_REED 26\n",
    )
    main = main.replace(
        "int beat_ruins_keeper = 0, beat_ruins_warden = 0, badge_quartz = 0;\n    int beat_quarry_driller = 0;\n",
        "int beat_ruins_keeper = 0, beat_ruins_warden = 0, badge_quartz = 0;\n"
        "    int beat_quarry_driller = 0;\n"
        "    int beat_marsh_bog = 0, beat_marsh_reed = 0, badge_opal = 0;\n",
    )
    main = main.replace(
        "ft[FLAG_BEAT_QUARRY_DRILLER] = &beat_quarry_driller;\n",
        "ft[FLAG_BEAT_QUARRY_DRILLER] = &beat_quarry_driller;\n"
        "        ft[FLAG_BEAT_MARSH_BOG] = &beat_marsh_bog;\n"
        "        ft[FLAG_BEAT_MARSH_REED] = &beat_marsh_reed;\n"
        "        ft[FLAG_BADGE_OPAL] = &badge_opal;\n",
    )
    main = main.replace(
        "beat_quarry_driller = save_flag_get(&sl, SAVE_FLAG_BEAT_QUARRY_DRILLER);\n",
        "beat_quarry_driller = save_flag_get(&sl, SAVE_FLAG_BEAT_QUARRY_DRILLER);\n"
        "                        beat_marsh_bog = save_flag_get(&sl, SAVE_FLAG_BEAT_MARSH_BOG);\n"
        "                        beat_marsh_reed = save_flag_get(&sl, SAVE_FLAG_BEAT_MARSH_REED);\n"
        "                        badge_opal = save_flag_get(&sl, SAVE_FLAG_BADGE_OPAL);\n",
    )
    main = main.replace(
        "beat_ruins_keeper = 0; beat_ruins_warden = 0; badge_quartz = 0;\n                beat_quarry_driller = 0;\n",
        "beat_ruins_keeper = 0; beat_ruins_warden = 0; badge_quartz = 0;\n"
        "                beat_quarry_driller = 0;\n"
        "                beat_marsh_bog = 0; beat_marsh_reed = 0; badge_opal = 0;\n",
    )
    main = main.replace(
        "save_flag_put(&sl, SAVE_FLAG_BEAT_QUARRY_DRILLER, beat_quarry_driller);\n",
        "save_flag_put(&sl, SAVE_FLAG_BEAT_QUARRY_DRILLER, beat_quarry_driller);\n"
        "                    save_flag_put(&sl, SAVE_FLAG_BEAT_MARSH_BOG, beat_marsh_bog);\n"
        "                    save_flag_put(&sl, SAVE_FLAG_BEAT_MARSH_REED, beat_marsh_reed);\n"
        "                    save_flag_put(&sl, SAVE_FLAG_BADGE_OPAL, badge_opal);\n",
    )

    win_block = (
        "                                else if(battle.trainer_kind == TRAINER_WSOLDIER_QUARRY_DRILLER) {\n"
        "                                    beat_quarry_driller = 1;\n"
        "                                    marks += 15;\n"
        "                                    battles++;\n"
        "                                    in_battle = 0;\n"
        "                                    enc_lock = 3;\n"
        "                                    seq_lines = TALK_QUARRY_DRILLER_WIN;\n"
        "                                    seq_len = TALK_LEN(TALK_QUARRY_DRILLER_WIN);\n"
        "                                    seq_beat = 0;\n"
        "                                    post_action = POST_NONE;\n"
        "                                }\n"
    )
    win_extra = win_block + (
        "                                else if(battle.trainer_kind == TRAINER_WSOLDIER_OPAL) {\n"
        "                                    badge_opal = 1;\n"
        "                                    marks += 17;\n"
        "                                    battles++;\n"
        "                                    in_battle = 0;\n"
        "                                    enc_lock = 3;\n"
        "                                    seq_lines = TALK_OPAL_WIN;\n"
        "                                    seq_len = TALK_LEN(TALK_OPAL_WIN);\n"
        "                                    seq_beat = 0;\n"
        "                                    post_action = POST_NONE;\n"
        "                                }\n"
        "                                else if(battle.trainer_kind == TRAINER_WSOLDIER_MARSH_BOG) {\n"
        "                                    beat_marsh_bog = 1;\n"
        "                                    marks += 11;\n"
        "                                    battles++;\n"
        "                                    in_battle = 0;\n"
        "                                    enc_lock = 3;\n"
        "                                    seq_lines = TALK_MARSH_BOG_WIN;\n"
        "                                    seq_len = TALK_LEN(TALK_MARSH_BOG_WIN);\n"
        "                                    seq_beat = 0;\n"
        "                                    post_action = POST_NONE;\n"
        "                                }\n"
        "                                else if(battle.trainer_kind == TRAINER_WSOLDIER_MARSH_REED) {\n"
        "                                    beat_marsh_reed = 1;\n"
        "                                    marks += 12;\n"
        "                                    battles++;\n"
        "                                    in_battle = 0;\n"
        "                                    enc_lock = 3;\n"
        "                                    seq_lines = TALK_MARSH_REED_WIN;\n"
        "                                    seq_len = TALK_LEN(TALK_MARSH_REED_WIN);\n"
        "                                    seq_beat = 0;\n"
        "                                    post_action = POST_NONE;\n"
        "                                }\n"
    )
    if "TRAINER_WSOLDIER_OPAL)" not in main:
        if win_block not in main:
            raise SystemExit("win block anchor missing")
        main = main.replace(win_block, win_extra)

    def case_block(post, kit, kind, msg):
        return (
            f"                                case {post}:\n"
            f"                                    battle.foe = mint_monster(TRAINER_KITS[{kit}].lead_sp, TRAINER_KITS[{kit}].lead_lv);\n"
            f"                                    battle.wild = 0;\n"
            f"                                    battle.trainer_kind = {kind};\n"
            f"                                    battle.phase = 0;\n"
            f"                                    {{ int n = s_cat(battle.msg[0], 0, \"{msg}\");\n"
            f"                                      battle.msg[0][n] = 0; }}\n"
            f"                                    battle.msg_n = 1; battle.msg_i = 0; battle.after = BAFTER_ITEM;\n"
            f"                                    battle.cur = 0;\n"
            f"                                    battle.mods_self_str = battle.mods_self_agl = battle.mods_self_spc = 0;\n"
            f"                                    battle.mods_foe_str = battle.mods_foe_agl = battle.mods_foe_spc = 0;\n"
            f"                                    battle.pend_str = battle.pend_agl = battle.pend_spc = 0;\n"
            f"                                    battle.pl_poisoned = battle.foe_poisoned = 0;\n"
            f"                                    battle.bench[0] = mint_monster(TRAINER_KITS[{kit}].bench_sp[0], TRAINER_KITS[{kit}].bench_lv[0]);\n"
            f"                                    battle.bench[1] = mint_monster(TRAINER_KITS[{kit}].bench_sp[1], TRAINER_KITS[{kit}].bench_lv[1]);\n"
            f"                                    battle.bench_n = TRAINER_KITS[{kit}].bench_n;\n"
            f"                                    battle.grew = 0;\n"
            f"                                    battle.pl = party[lead];\n"
            f"                                    in_battle = 1;\n"
            f"                                    break;\n"
        )

    if "POST_WSOLDIER_OPAL:" not in main:
        insert = (
            case_block("POST_WSOLDIER_OPAL", "KIT_OPAL", "TRAINER_WSOLDIER_OPAL", "OPAL SENDS GLASSWISP")
            + case_block("POST_WSOLDIER_MARSH_BOG", "KIT_MARSH_BOG", "TRAINER_WSOLDIER_MARSH_BOG", "BOGWALKER SENDS PEATLING")
            + case_block("POST_WSOLDIER_MARSH_REED", "KIT_MARSH_REED", "TRAINER_WSOLDIER_MARSH_REED", "REEDGUARD SENDS FENWISP")
        )
        q_end = (
            "                                    battle.bench_n = TRAINER_KITS[KIT_QUARRY_DRILLER].bench_n;\n"
            "                                    battle.grew = 0;\n"
            "                                    battle.pl = party[lead];\n"
            "                                    in_battle = 1;\n"
            "                                    break;\n"
            "                                case POST_WSOLDIER_WARDEN:"
        )
        if q_end not in main:
            raise SystemExit("POST_WSOLDIER_WARDEN anchor missing")
        main = main.replace(
            q_end,
            "                                    battle.bench_n = TRAINER_KITS[KIT_QUARRY_DRILLER].bench_n;\n"
            "                                    battle.grew = 0;\n"
            "                                    battle.pl = party[lead];\n"
            "                                    in_battle = 1;\n"
            "                                    break;\n"
            + insert
            + "                                case POST_WSOLDIER_WARDEN:",
            1,
        )

    pend = (
        "else if(npc_pending == NPC_PENDING_QUARRY_DRILLER)\n"
        "                                    post_action = POST_WSOLDIER_QUARRY_DRILLER;\n"
    )
    pend_extra = (
        pend
        + "                                else if(npc_pending == NPC_PENDING_OPAL)\n"
        + "                                    post_action = POST_WSOLDIER_OPAL;\n"
        + "                                else if(npc_pending == NPC_PENDING_MARSH_BOG)\n"
        + "                                    post_action = POST_WSOLDIER_MARSH_BOG;\n"
        + "                                else if(npc_pending == NPC_PENDING_MARSH_REED)\n"
        + "                                    post_action = POST_WSOLDIER_MARSH_REED;\n"
    )
    if "NPC_PENDING_OPAL)" not in main:
        if pend not in main:
            raise SystemExit("pending map anchor missing")
        main = main.replace(pend, pend_extra)

    path.write_text(main)
    print("main.c ok", main.count("TRAINER_WSOLDIER_OPAL"), main.count("beat_marsh_bog"))

def patch_cw():
    p = Path("CURRENT_WORK.md")
    t = p.read_text()
    t = t.replace(
        "Dreamcast PENDING dispatch still thin (Claude noted for marsh/opal).",
        "Dreamcast PENDING dispatch for marshBog/marshReed/opal wired (Grok C).",
    )
    t = t.replace(
        "Quartz + Opal wardens live (web). Overworld NPC blit is JSON-driven. Quarry Driller wired by Claude A.",
        "Quartz + Opal + marsh trainers live on web and Dreamcast PENDING. Quarry Driller by Claude A.",
    )
    p.write_text(t)
    print("CURRENT_WORK ok")

if __name__ == "__main__":
    patch_bake()
    patch_main()
    patch_cw()
