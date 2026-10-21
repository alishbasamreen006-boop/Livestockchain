import io
from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import qrcode
import streamlit as st

import auth, db, seed, service, ui
from blockchain import Chain
from livestock import SPECIES, MILK_SPECIES, PLURAL, DEFAULT_MILK_RATE

st.set_page_config(page_title="LivestockChain - Farm Management", page_icon="🐐", layout="wide")
ui.inject()
GREENS = ["#2E7D4F", "#E3A72F", "#3B82C4", "#8C6D46", "#7DBE6B", "#D9534F", "#6A5ACD"]


@st.cache_resource
def get_chain():
    db.init()
    chain = Chain()
    service.resync(chain)   # re-anchor stored hashes if using the local test chain
    return chain

chain = get_chain()
db.init()
auth.ensure_demo_users()


def qr_png(url):
    buf = io.BytesIO(); qrcode.make(url).save(buf, format="PNG"); return buf.getvalue()

def vacc_status(tag):
    r = db.q("SELECT next_due FROM records WHERE tag=? AND next_due!='' ORDER BY id DESC LIMIT 1", (tag,))
    if not r: return "No vaccine schedule", "none"
    days = (date.fromisoformat(r[0]["next_due"]) - date.today()).days
    if days < 0: return f"Vaccine OVERDUE ({-days} days)", "bad"
    if days <= 14: return f"Vaccine due in {days} days", "soon"
    return "Vaccinations OK", "ok"

def style_fig(fig):
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=10, r=10, t=50, b=10),
                      colorway=GREENS, title_font_size=16)
    return fig

def sheds():
    return [r["shed"] for r in db.q("SELECT DISTINCT shed FROM animals WHERE shed IS NOT NULL ORDER BY shed")]

def gallery(items, per_row=4):
    cols = st.columns(per_row)
    for i, a in enumerate(items):
        s, css = vacc_status(a["tag"])
        with cols[i % per_row]: ui.animal_card(a, s, css)

def verify_view(tag):
    animal = db.q("SELECT * FROM animals WHERE tag=?", (tag,))
    if not animal:
        st.error(f"No animal found with tag '{tag}'."); return
    a = animal[0]
    results, missing, all_ok = service.verify(chain, tag)
    left, right = st.columns([1, 2])
    with left:
        s, css = vacc_status(tag); ui.animal_card(a, s, css)
    with right:
        if all_ok:
            st.success("✅ HISTORY VERIFIED: every record matches its blockchain fingerprint.")
        else:
            st.error("❌ WARNING: some records do NOT match the blockchain. This history may have been altered.")
        if results:
            df = pd.DataFrame(results).drop(columns=["id", "tx"])
            df["status"] = df["status"].map({"VERIFIED": "✅ VERIFIED", "TAMPERED": "❌ TAMPERED"})
            st.dataframe(df, width="stretch", hide_index=True)
        for m in missing:
            st.warning(f"The blockchain holds a {m['event_type']} event that is missing or changed in the database.")
        with st.expander("Blockchain proof (technical)"):
            st.write("Mode:", "Public testnet" if chain.live else "Local test chain (demo)")
            st.write("Contract address:", chain.contract.address)
            st.dataframe(pd.DataFrame(chain.get_events(tag)), width="stretch", hide_index=True)

# ======================= PUBLIC PAGE (QR scan, no login) =======================
if "tag" in st.query_params:
    ui.pagehead("🔍", "Verified Animal History", "This history has been checked against blockchain fingerprints.")
    verify_view(st.query_params["tag"]); st.stop()

# ======================= LOGIN / REGISTER =======================
if "user" not in st.session_state:
    ui.hero("LivestockChain", "Trusted digital records for every animal on the farm: health, milk, profit and sales, secured by blockchain.")
    _, mid, _ = st.columns([1, 1.6, 1])
    with mid:
        st.markdown('<div class="loginbox">', unsafe_allow_html=True)
        t_login, t_reg = st.tabs(["🔐 Login", "📝 New Account"])
        with t_login:
            with st.form("login"):
                u = st.text_input("Username"); p = st.text_input("Password", type="password")
                if st.form_submit_button("Login", type="primary", use_container_width=True):
                    user = auth.login(u, p)
                    if user:
                        st.session_state.user = user; st.rerun()
                    else:
                        st.error("Wrong username or password.")
            st.markdown('<div class="demo"><b>Demo accounts:</b><br>Farm Owner: <code>owner</code> / <code>owner123</code><br>'
                        'Veterinarian: <code>vet</code> / <code>vet123</code><br>Buyer: <code>buyer</code> / <code>buyer123</code></div>', unsafe_allow_html=True)
        with t_reg:
            with st.form("register", clear_on_submit=True):
                fn = st.text_input("Full name"); un = st.text_input("Username (a-z, 0-9)")
                role = st.selectbox("I am a", auth.ROLES)
                p1 = st.text_input("Password (at least 6 characters)", type="password"); p2 = st.text_input("Repeat password", type="password")
                if st.form_submit_button("Create account", type="primary", use_container_width=True):
                    if p1 != p2: st.error("The two passwords do not match.")
                    else:
                        ok, msg = auth.create_user(un, fn, role, p1)
                        (st.success if ok else st.error)(msg)
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ======================= MAIN APP (logged in) =======================
user = st.session_state.user
role = user["role"]
st.sidebar.markdown('<div class="brand"><b>🐐 LivestockChain</b><br><span>Blockchain Livestock Management</span></div>', unsafe_allow_html=True)
st.sidebar.markdown(f'<div class="userchip"><b>{user["full_name"]}</b><br><small>{role} &middot; @{user["username"]}</small></div>', unsafe_allow_html=True)
menus = {"Farm Owner": ["🏠 Dashboard", "🐄 Animal Registry", "💉 Health Records", "🥛 Milk & Expenses", "🤝 Sell / Transfer", "🔍 Verify & QR"],
         "Veterinarian": ["💉 Health Records", "🔍 Verify & QR"], "Buyer": ["🔍 Verify & QR"]}[role]
page = st.sidebar.radio("Menu", menus, label_visibility="collapsed")
st.sidebar.caption("⛓️ Blockchain: " + ("Public testnet" if chain.live else "Local test chain (demo mode)"))
if role == "Farm Owner" and st.sidebar.button("Load dummy demo data", use_container_width=True):
    seed.seed(chain); st.sidebar.success("Dummy data loaded."); st.rerun()
if st.sidebar.button("Logout", use_container_width=True):
    del st.session_state["user"]; st.rerun()

animals = db.q("SELECT * FROM animals ORDER BY tag")
tags = [a["tag"] for a in animals]

# ---------- Dashboard ----------
if page.endswith("Dashboard"):
    first = user["full_name"].split()[0] if user["full_name"] else ""
    ui.hero(f"Welcome back, {first}!", "Today on your farm: animals, milk, expenses and profit at a glance.")
    if not animals:
        st.info("No data yet. Press 'Load dummy demo data' in the sidebar, or register your first animal.")
    else:
        today = date.today(); since7 = str(today - timedelta(days=7)); month = str(today - timedelta(days=30))
        milk7 = db.q("SELECT COALESCE(SUM(liters),0) s FROM milk WHERE day>=?", (since7,))[0]["s"]
        exp = db.q("SELECT COALESCE(SUM(amount),0) s FROM expenses WHERE day>=?", (month,))[0]["s"]
        inc = db.q("SELECT COALESCE(SUM(amount),0) s FROM income WHERE day>=?", (month,))[0]["s"]
        active = [a for a in animals if a["status"] == "Active"]
        flags = [(a, *vacc_status(a["tag"])) for a in active]
        needs = [f for f in flags if f[2] in ("bad", "soon")]
        overdue = [f for f in needs if f[2] == "bad"]

        if overdue:
            names = ", ".join(f"<b>{f[0]['name']}</b> ({f[0]['tag']})" for f in overdue[:6]) + (" and more" if len(overdue) > 6 else "")
            ui.alert(f"⚠️ {len(overdue)} animal(s) have overdue vaccinations: {names}. Open Health Records to update them.", "bad")
        else:
            ui.alert("✅ All vaccinations are up to date.", "ok")

        k = st.columns(4)
        with k[0]: ui.kpi("Active animals", len(active), f"{len(set(a['species'] for a in active))} species on the farm")
        with k[1]: ui.kpi("Milk (7 days)", f"{milk7:,.0f} L", "all milking animals", "blue")
        with k[2]: ui.kpi("Expenses (30d)", f"Rs {exp:,.0f}", "feed, labour, medicine", "gold")
        with k[3]: ui.kpi("Profit (30d)", f"Rs {inc - exp:,.0f}", "income minus expenses")

        st.markdown("### Your herd")
        present = [s for s in SPECIES if any(a["species"] == s for a in active)]
        tiles = st.columns(len(present))
        for col, sp in zip(tiles, present):
            group = [a for a in active if a["species"] == sp]
            if sp in MILK_SPECIES:
                tl = db.q("SELECT COALESCE(SUM(liters),0) s FROM milk WHERE day>=? AND tag IN (%s)" % ",".join("?" * len(group)), (since7, *[g["tag"] for g in group]))[0]["s"]
                sub = f"{tl / 7:,.0f} L milk per day"
            else:
                sub = f"avg {sum(g['weight_kg'] or 0 for g in group) / len(group):,.0f} kg"
            with col: ui.species_tile(sp, len(group), sub)

        st.markdown("### Highlights")
        l, r = st.columns(2)
        top = db.q("SELECT m.tag, SUM(m.liters) s FROM milk m WHERE m.day>=? GROUP BY m.tag ORDER BY s DESC LIMIT 1", (since7,))
        with l:
            if top:
                a = db.q("SELECT * FROM animals WHERE tag=?", (top[0]["tag"],))[0]
                ui.star_card(a, "🏆 Top milk producer this week", f"{top[0]['s']:,.0f} L", f"{a['species']} &middot; {a['breed']} &middot; {a.get('shed') or ''}")
            else:
                st.info("Milk entries will show your top producer here.")
        with r:
            if needs:
                st.markdown("**Vaccinations needing attention**")
                for a, s, css in needs[:5]:
                    ui.alert(f"<b>{a['name']}</b> ({a['species']}, {a['tag']}): {s}", "bad" if css == "bad" else "ok")
            else:
                st.markdown("**Vaccinations needing attention**"); st.caption("Nothing due in the next 14 days.")

        c1, c2 = st.columns(2)
        milk = pd.DataFrame(db.q("SELECT m.day, a.species, SUM(m.liters) liters FROM milk m JOIN animals a ON a.tag=m.tag GROUP BY m.day, a.species ORDER BY m.day"))
        if not milk.empty:
            c1.plotly_chart(style_fig(px.area(milk, x="day", y="liters", color="species", title="Daily milk production by species (litres)")), width="stretch")
        ex = pd.DataFrame(db.q("SELECT category, SUM(amount) amount FROM expenses GROUP BY category"))
        if not ex.empty:
            c2.plotly_chart(style_fig(px.pie(ex, names="category", values="amount", hole=.5, title="Where the money goes")), width="stretch")

        st.markdown("### All animals")
        f1, f2 = st.columns(2)
        pick_sp = f1.multiselect("Species", SPECIES, default=[], placeholder="All species")
        pick_shed = f2.selectbox("Shed / group", ["All sheds"] + sheds())
        shown = [a for a in animals if (not pick_sp or a["species"] in pick_sp) and (pick_shed == "All sheds" or a.get("shed") == pick_shed)]
        gallery(shown)

# ---------- Animal registry ----------
elif page.endswith("Animal Registry"):
    ui.pagehead("🐄", "Animal Registry", "A digital ID for every animal. The proof goes to the blockchain as soon as you register.")
    gallery(animals)
    st.markdown("### ➕ Register a new animal")
    with st.form("reg", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        tag = c1.text_input("Tag ID", help="Suggested codes: CW cow, BF buffalo, GT goat, SH sheep, BL bull, CF calf (e.g. GT-006)")
        name = c2.text_input("Name"); species = c3.selectbox("Species", SPECIES)
        breed = c1.text_input("Breed"); age = c2.number_input("Age (months)", 0, 300, 24)
        weight = c3.number_input("Weight (kg)", 0.0, 1500.0, 40.0)
        s1, s2 = st.columns(2)
        shed_pick = s1.selectbox("Shed / group", sheds() + ["New shed..."]); shed_new = s2.text_input("New shed name (only if 'New shed...' is chosen)")
        owner = st.text_input("Owner", user["full_name"])
        if st.form_submit_button("Register and save to blockchain", type="primary"):
            shed = shed_new.strip() if shed_pick == "New shed..." else shed_pick
            if not tag.strip(): st.error("Tag ID is required.")
            elif tag.strip() in tags: st.error("This tag already exists.")
            elif not shed: st.error("Please choose or enter a shed name.")
            else:
                db.run("INSERT INTO animals(tag,name,species,breed,age_months,weight_kg,owner,created,shed) VALUES(?,?,?,?,?,?,?,?,?)",
                       (tag.strip(), name, species, breed, age, weight, owner, str(date.today()), shed))
                _, h, tx = service.add_record(chain, tag.strip(), "REGISTRATION", date.today(), f"{species} {breed}, {age} months, {weight} kg, {shed}", owner)
                st.success(f"Registered. Fingerprint: {h[:16]}...  Transaction: {tx[:18]}..."); st.rerun()

# ---------- Health records ----------
elif page.endswith("Health Records"):
    ui.pagehead("💉", "Health & Vaccination Records", "The vet saves a record and its fingerprint is signed on the blockchain.")
    if not tags:
        st.info("Register an animal first.")
    else:
        t1, t2 = st.tabs(["Single animal", "Whole shed (bulk)"])
        with t1:
            with st.form("health", clear_on_submit=True):
                c1, c2 = st.columns(2)
                tag = c1.selectbox("Animal", tags); rtype = c2.selectbox("Record type", ["VACCINATION", "TREATMENT", "BREEDING", "CHECKUP"])
                rdate = c1.date_input("Date", date.today()); nxt = c2.date_input("Next due date (optional)", value=None)
                details = st.text_area("Details (vaccine name, illness, medicine...)")
                by = st.text_input("Veterinarian / recorded by", user["full_name"] if role == "Veterinarian" else "")
                if st.form_submit_button("Save and sign on blockchain", type="primary"):
                    if not details.strip() or not by.strip(): st.error("Details and the vet's name are required.")
                    else:
                        _, h, tx = service.add_record(chain, tag, rtype, rdate, details, by, next_due=nxt or "")
                        st.success(f"Saved. Fingerprint {h[:16]}... transaction {tx[:18]}...")
        with t2:
            st.caption("Give the same vaccination or checkup to every selected animal. Each animal still gets its own blockchain record.")
            with st.form("bulk", clear_on_submit=True):
                b1, b2 = st.columns(2)
                shed = b1.selectbox("Shed / group", ["All sheds"] + sheds()); spp = b2.multiselect("Only these species (optional)", SPECIES)
                btype = b1.selectbox("Record type", ["VACCINATION", "CHECKUP", "TREATMENT"], key="bt")
                bdate = b2.date_input("Date", date.today(), key="bd"); bnext = b1.date_input("Next due date (optional)", value=None, key="bn")
                bdetails = st.text_area("Details (e.g. PPR vaccine, batch PPR-2026-B)", key="bdet")
                bby = st.text_input("Veterinarian / recorded by", user["full_name"] if role == "Veterinarian" else "", key="bby")
                targets = [a for a in animals if a["status"] == "Active" and (shed == "All sheds" or a.get("shed") == shed) and (not spp or a["species"] in spp)]
                st.write(f"Matching animals: **{len(targets)}**")
                if st.form_submit_button("Save for all matching animals", type="primary"):
                    if not bdetails.strip() or not bby.strip(): st.error("Details and the vet's name are required.")
                    elif not targets: st.error("No animals match this selection.")
                    else:
                        with st.spinner("Writing to blockchain..."):
                            for a in targets:
                                service.add_record(chain, a["tag"], btype, bdate, bdetails, bby, next_due=bnext or "")
                        st.success(f"Saved {len(targets)} records on the blockchain.")
        st.markdown("### Recent records")
        rec = db.q("SELECT id, tag, rec_type, rec_date, details, next_due, by_user FROM records ORDER BY id DESC LIMIT 100")
        if rec: st.dataframe(pd.DataFrame(rec), width="stretch", hide_index=True)

# ---------- Milk & expenses ----------
elif page.endswith("Milk & Expenses"):
    ui.pagehead("🥛", "Milk, Expenses & Profit per Animal", "This data stays in the database. Only key events go to the blockchain.")
    t1, t2, t3 = st.tabs(["🥛 Milk entry", "💸 Expenses / Income", "📊 Profit per animal"])
    milkers = [a["tag"] for a in animals if a["species"] in MILK_SPECIES and a["status"] == "Active"]
    with t1:
        st.caption("Milk tracking is available for cows, buffaloes and goats.")
        with st.form("milk", clear_on_submit=True):
            tag = st.selectbox("Animal", milkers) if milkers else None
            day = st.date_input("Date", date.today()); liters = st.number_input("Litres", 0.0, 60.0, 5.0)
            if st.form_submit_button("Save milk", type="primary") and tag:
                db.run("INSERT INTO milk(tag,day,liters) VALUES(?,?,?)", (tag, str(day), liters)); st.success("Saved.")
    with t2:
        with st.form("exp", clear_on_submit=True):
            kind = st.radio("Type", ["Expense", "Income"], horizontal=True)
            cat = st.selectbox("Category", ["Feed", "Medicine", "Labour", "Electricity/Water", "Transport", "Milk sale", "Animal sale", "Wool / by-product", "Other"])
            amount = st.number_input("Amount (Rs)", 0.0, 10_000_000.0, 1000.0)
            tag = st.selectbox("For which animal (optional)", [""] + tags); day = st.date_input("Date ", date.today())
            if st.form_submit_button("Save", type="primary"):
                if kind == "Expense": db.run("INSERT INTO expenses(day,category,amount,tag,note) VALUES(?,?,?,?,?)", (str(day), cat, amount, tag or None, ""))
                else: db.run("INSERT INTO income(day,source,amount,tag) VALUES(?,?,?,?)", (str(day), cat, amount, tag or None))
                st.success("Saved.")
    with t3:
        st.caption("Assumed milk prices. Edit them to match your farm.")
        pc = st.columns(3); rate = {sp: pc[i].number_input(f"{sp} milk (Rs per litre)", 0.0, 1000.0, DEFAULT_MILK_RATE[sp]) for i, sp in enumerate(MILK_SPECIES)}
        days = st.slider("Period (days)", 7, 90, 30); since = str(date.today() - timedelta(days=days))
        n_active = max(len([a for a in animals if a["status"] == "Active"]), 1)
        shared = db.q("SELECT COALESCE(SUM(amount),0) s FROM expenses WHERE tag IS NULL AND day>=?", (since,))[0]["s"] / n_active
        rows = []
        for a in animals:
            liters = db.q("SELECT COALESCE(SUM(liters),0) s FROM milk WHERE tag=? AND day>=?", (a["tag"], since))[0]["s"]
            direct = db.q("SELECT COALESCE(SUM(amount),0) s FROM expenses WHERE tag=? AND day>=?", (a["tag"], since))[0]["s"]
            sales = db.q("SELECT COALESCE(SUM(amount),0) s FROM income WHERE tag=? AND day>=?", (a["tag"], since))[0]["s"]
            rev = liters * rate.get(a["species"], 0) + sales
            rows.append({"Animal": a["tag"], "Name": a["name"], "Species": a["species"], "Milk (L)": round(liters, 1), "Revenue (Rs)": round(rev),
                         "Direct cost (Rs)": round(direct), "Shared cost share (Rs)": round(shared), "Net (Rs)": round(rev - direct - shared)})
        if rows:
            df = pd.DataFrame(rows); st.dataframe(df, width="stretch", hide_index=True)
            st.plotly_chart(style_fig(px.bar(df, x="Name", y="Net (Rs)", color="Species", title="Net profit per animal")), width="stretch")
            st.caption("Revenue is milk sold plus any sale recorded against that animal. Shared costs (feed, labour...) are split equally across active animals. This is a simple estimate.")

# ---------- Sell / transfer ----------
elif page.endswith("Sell / Transfer"):
    ui.pagehead("🤝", "Sell or Transfer Ownership", "The sale is written to the blockchain so the buyer can fully trust the history.")
    active = [a for a in animals if a["status"] == "Active"]
    if not active: st.info("No active animals.")
    else:
        with st.form("sale", clear_on_submit=True):
            tag = st.selectbox("Animal", [a["tag"] for a in active]); buyer = st.text_input("Buyer's name")
            price = st.number_input("Price (Rs)", 0.0, 100_000_000.0, 50000.0); sdate = st.date_input("Date", date.today())
            if st.form_submit_button("Complete sale and write to blockchain", type="primary"):
                if not buyer.strip(): st.error("Buyer's name is required.")
                else:
                    owner = db.q("SELECT owner FROM animals WHERE tag=?", (tag,))[0]["owner"]
                    service.add_record(chain, tag, "SALE", sdate, f"Sold by {owner} to {buyer} for Rs {price:,.0f}", owner)
                    db.run("UPDATE animals SET owner=? WHERE tag=?", (buyer, tag))
                    db.run("INSERT INTO income(day,source,amount,tag) VALUES(?,?,?,?)", (str(sdate), "Animal sale", price, tag))
                    st.success(f"{tag} now belongs to {buyer}. The buyer can scan the QR code to see the full history.")

# ---------- Verify & QR ----------
elif page.endswith("Verify & QR"):
    ui.pagehead("🔍", "Verify History & QR Code", "Choose an animal tag, create its QR code, and check the history against the blockchain.")
    if not tags: st.info("No animals yet.")
    else:
        tag = st.selectbox("Animal tag", tags)
        c1, c2 = st.columns([1, 3])
        with c1:
            base = st.text_input("App address inside the QR", "http://localhost:8501",
                                 help="On demo day use your laptop's Wi-Fi IP (e.g. http://192.168.1.5:8501) so a phone can open it.")
            link = f"{base}/?tag={tag}"
            st.image(qr_png(link), caption=f"Scan: {tag}", width=210)
            st.download_button("Download QR (PNG)", qr_png(link), file_name=f"{tag}_qr.png", mime="image/png")
        with c2: verify_view(tag)
        if role == "Farm Owner":
            with st.expander("🧪 Demo: simulate tampering with the database"):
                st.caption("This changes a record directly in the database, outside the app. Then check the verification again.")
                recs = db.q("SELECT id, rec_type, details FROM records WHERE tag=? ORDER BY id", (tag,))
                if recs:
                    pick = st.selectbox("Which record to alter", recs, format_func=lambda r: f"#{r['id']} {r['rec_type']}: {r['details'][:50]}")
                    if st.button("Alter record"):
                        db.run("UPDATE records SET details=? WHERE id=?", (pick["details"] + " [ALTERED]", pick["id"])); st.rerun()
