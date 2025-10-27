# --- Modify donut size + layout adjustments ---

def donut_svg(value_pct, ring_color, track="#EFEFEF", size=120, stroke=12, label_text=None):
    """Bigger donut for visibility"""
    pct = clamp_pct(abs(value_pct))
    cx = cy = size // 2
    r = (size - stroke) // 2
    full = 2 * math.pi * r
    gap = 0.03 * full
    value_len = (pct / 100.0) * (full - gap)

    label = f"{value_pct:.0f}%" if label_text is None else label_text

    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{track}" stroke-width="{stroke}" stroke-linecap="round"
              stroke-dasharray="{full-gap} {gap}" transform="rotate(-90 {cx} {cy})" />
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ring_color}" stroke-width="{stroke}" stroke-linecap="round"
              stroke-dasharray="{value_len} {full}" transform="rotate(-90 {cx} {cy})" />
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
            font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial"
            font-size="22" font-weight="700" fill="#2F2F2F">{label}</text>
    </svg>
    """

# --- CSS section (replace only inside your CSS block) ---
CSS = """
<style>
:root{
  --shadow: 0 10px 24px rgba(16,24,40,.06), 0 1px 2px rgba(16,24,40,.05);
  --radius: 16px;
  --font: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}
*{box-sizing:border-box}
.kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:28px;margin-top:6px}
.kpi-card{
  position:relative;
  background:var(--card-bg);
  border-radius:var(--radius);
  box-shadow:var(--shadow);
  padding:22px 22px 28px;
  min-height:270px;
  display:flex;
  flex-direction:column;
  justify-content:space-between;
}
.kpi-top{
  display:flex;
  align-items:center;
  justify-content:space-between;
  margin-bottom:10px;
}
.kpi-title{
  font-family:var(--font);
  font-size:16px;
  letter-spacing:.02em;
  font-weight:700;
  color:#3A3A3A;
  text-transform:uppercase;
}
.kpi-ring-wrap{
  width:120px;
  height:120px;
  margin-top:-8px; /* shift donut slightly up */
}
.kpi-value{
  font-family:var(--font);
  font-size:58px;
  font-weight:800;
  color:#121212;
  line-height:1;
  margin-top:-12px; /* shift value upward slightly */
  text-align:left;
}
.kpi-divider{
  height:1px;
  width:100%;
  background:rgba(0,0,0,.08);
  margin:4px 0 10px;
}
.kpi-meta{
  display:flex;
  align-items:center;
  justify-content:space-between;
  font-family:var(--font);
  margin-bottom:10px;
}
.kpi-meta .label{
  color:#475467;
  font-weight:600;
  margin-right:6px;
}
.kpi-btn{
  display:flex;
  justify-content:center;
  margin-top:8px;
}
.kpi-btn button{
  background:#fff;
  color:var(--btn-color);
  border:2px solid var(--btn-color);
  font-family:var(--font);
  font-weight:700;
  font-size:16px;
  padding:10px 28px;
  border-radius:12px;
  box-shadow:0 1px 0 rgba(16,24,40,.05);
  transition:all .15s ease;
  cursor:pointer;
}
.kpi-btn button:hover{
  box-shadow:0 4px 10px rgba(16,24,40,.08);
  transform:translateY(-1px);
}
.block{
  background:#fff;
  border-radius:20px;
  box-shadow:var(--shadow);
  padding:26px 28px;
  margin-bottom:22px;
}
.h-title{
  font-family:var(--font);
  font-size:46px;
  font-weight:800;
  margin:0 0 10px;
  color:#101828;
}
.h-sub{
  font-family:var(--font);
  font-size:18px;
  color:#475467;
  margin:0;
}
@media(max-width:1200px){
  .kpi-grid{grid-template-columns:1fr}
  .kpi-card{min-height:260px}
}
</style>
"""
