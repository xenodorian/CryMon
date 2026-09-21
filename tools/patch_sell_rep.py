#!/usr/bin/env python3
"""Sell price = half of buy, scaled +1% per +rep / -1% per -rep, floor 1 mark."""
from pathlib import Path

# --- Web engine.ts ---
ep = Path("src/game/engine.ts")
e = ep.read_text()

if "shopSellPrice(" in e:
    print("web shopSellPrice already present")
else:
    anchor = """	shopBuyPrice(id) {
		const base = ITEMS[id].buy;
		const r = LOGIC.reputation || {};
		const pos = r.pricePosPct ?? 1;
		const neg = r.priceNegPct ?? 5;
		const minP = r.minPrice ?? 1;
		if (this.reputation > 0) return Math.max(minP, Math.floor(base * (100 - this.reputation * pos) / 100));
		if (this.reputation < 0) return Math.max(minP, Math.floor(base * (100 + (-this.reputation) * neg) / 100));
		return base;
	}"""
    insert = anchor + """
	/** Half of list buy price, then +1% per +rep / -1% per -rep. Never below 1 mark. */
	shopSellPrice(id) {
		const base = Math.floor((ITEMS[id].buy || 0) / 2);
		const minP = LOGIC.reputation?.minPrice ?? 1;
		const r = this.reputation | 0;
		return Math.max(minP, Math.floor(base * (100 + r) / 100));
	}"""
    if anchor not in e:
        raise SystemExit("shopBuyPrice anchor missing")
    e = e.replace(anchor, insert, 1)
    print("web shopSellPrice added")

# Use sell price in credit + UI
if "this.marks += this.shopSellPrice(id)" not in e:
    if "this.marks += ITEMS[id].sell" not in e:
        raise SystemExit("sell credit anchor missing")
    e = e.replace("this.marks += ITEMS[id].sell", "this.marks += this.shopSellPrice(id)", 1)
    print("web sell credit")
else:
    print("web sell credit already")

if "${this.shopSellPrice(id)}m" not in e:
    if "`${ITEMS[id].sell}m`" not in e:
        raise SystemExit("sell UI price anchor missing")
    e = e.replace("`${ITEMS[id].sell}m`", "`${this.shopSellPrice(id)}m`", 1)
    print("web sell UI")
else:
    print("web sell UI already")

ep.write_text(e)

# --- Dreamcast main.c ---
mp = Path("ports/dreamcast/src/main.c")
m = mp.read_text()

if "shop_sell_price(" in m:
    print("dc shop_sell_price already")
else:
    # insert after shop_buy_price function - find end of function after LOGIC_REP_MIN_PRICE return base
    old = """static int shop_buy_price(int base, int reputation) {
    int p;
    if(reputation > 0) {
        p = base * (100 - reputation * LOGIC_REP_PRICE_POS_PCT) / 100;
        if(p < LOGIC_REP_MIN_PRICE) p = LOGIC_REP_MIN_PRICE;
        return p;
    }
    if(reputation < 0) {
        p = base * (100 + (-reputation) * LOGIC_REP_PRICE_NEG_PCT) / 100;
        if(p < LOGIC_REP_MIN_PRICE) p = LOGIC_REP_MIN_PRICE;
        return p;
    }
    return base;
}"""
    new = old + """

/* Half of list buy price, then +1% per +rep / -1% per -rep. Floor 1 mark. */
static int shop_sell_price(int buy, int reputation) {
    int base = buy / 2;
    int p = base * (100 + reputation) / 100;
    if(p < LOGIC_REP_MIN_PRICE) p = LOGIC_REP_MIN_PRICE;
    return p;
}"""
    if old not in m:
        raise SystemExit("shop_buy_price anchor missing")
    m = m.replace(old, new, 1)
    print("dc shop_sell_price added")

# display price in draw_shop
old_price = "int price = sell_tab ? ITEMS[idx].sell : shop_buy_price(ITEMS[idx]"
# need fuller line
import re
m2, n = re.subn(
    r"int price = sell_tab \? ITEMS\[idx\]\.sell : shop_buy_price\(ITEMS\[idx\]\.buy, reputation\);",
    "int price = sell_tab ? shop_sell_price(ITEMS[idx].buy, reputation) : shop_buy_price(ITEMS[idx].buy, reputation);",
    m,
    count=1,
)
if n:
    m = m2
    print("dc draw price")
else:
    if "shop_sell_price(ITEMS[idx].buy, reputation)" in m:
        print("dc draw price already")
    else:
        raise SystemExit("dc draw price anchor missing")

m2, n = re.subn(
    r"marks \+= ITEMS\[idx\]\.sell;",
    "marks += shop_sell_price(ITEMS[idx].buy, reputation);",
    m,
    count=1,
)
if n:
    m = m2
    print("dc sell credit")
else:
    if "marks += shop_sell_price" in m:
        print("dc sell credit already")
    else:
        raise SystemExit("dc sell credit anchor missing")

mp.write_text(m)
print("done")
