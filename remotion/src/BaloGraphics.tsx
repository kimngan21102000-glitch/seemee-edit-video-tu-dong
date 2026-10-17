/** Gói đồ hoạ "balo" (thời trang, túi, balo) — bản KHUNG cơ bản, sẽ tinh chỉnh khi có source balo đầu tiên.
 *  Màu theo preset (PALETTE), cỡ/khoảng cách giống các thẻ chung để pipeline né mặt + đặt chỗ như nhau
 *  (vf/placement.py GRAPHIC_H_PX/GRAPHIC_W_PX: size_fit 330×620, compartments 520×600, badge 260×560). */
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { FONT_STACK, GraphicItem, PALETTE, parseRich, plainText } from "./types";

const FADE = 8;

const useFade = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return interpolate(frame, [0, FADE, durationInFrames - FADE, durationInFrames], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

const Rich: React.FC<{ text: string }> = ({ text }) => (
  <>
    {parseRich(text).map((p, i) => (
      <span key={i} style={{ color: p.tone === "accent" ? PALETTE.pink : p.tone === "accent2" ? PALETTE.accent2 : undefined }}>
        {p.t}
      </span>
    ))}
  </>
);

/** Kích thước / sức chứa: laptop trượt vào balo (đường nét), nhãn `label` ("VỪA LAPTOP *15,6″*"), dòng phụ `sub`
 *  (kích thước "45 × 30 × 15 cm"). */
export const SizeFitFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useFade();
  const bag = spring({ frame, fps, config: { damping: 14, stiffness: 180 } });
  const slide = spring({ frame: frame - 10, fps, config: { damping: 16, stiffness: 120 } });
  const tick = spring({ frame: frame - 26, fps, config: { damping: 9, stiffness: 240 } });
  const lab = spring({ frame: frame - 6, fps, config: { damping: 13, stiffness: 200 } });
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div style={{ position: "absolute", top: `${(item.y ?? 0.45) * 100}%`, width: 620, display: "flex",
                    alignItems: "center", gap: 18, fontFamily: FONT_STACK }}>
        <div style={{ position: "relative", width: 200, height: 250, flex: "0 0 200px", scale: interpolate(bag, [0, 1], [0.7, 1]),
                      opacity: Math.min(1, bag * 1.5) }}>
          <svg width={200} height={250} viewBox="0 0 200 250" style={{ filter: "drop-shadow(0 10px 16px rgba(0,0,0,0.35))" }}>
            {/* laptop: trượt từ trên xuống vào miệng balo */}
            <g transform={`translate(0 ${interpolate(slide, [0, 1], [-120, 0])})`}>
              <rect x={48} y={30} width={104} height={74} rx={6} fill="#E9EEF5" stroke="#9AA6B5" strokeWidth={4} />
              <rect x={56} y={38} width={88} height={56} rx={3} fill="#2B3440" />
            </g>
            {/* balo: thân bo tròn, quai, túi trước */}
            <path d="M40 90 Q40 60 70 60 L130 60 Q160 60 160 90 L160 225 Q160 240 145 240 L55 240 Q40 240 40 225 Z"
                  fill={PALETTE.plum} stroke={PALETTE.pink} strokeWidth={5} />
            <path d="M75 60 Q75 30 100 30 Q125 30 125 60" fill="none" stroke={PALETTE.pink} strokeWidth={6} />
            <rect x={62} y={150} width={76} height={62} rx={14} fill="none" stroke="rgba(255,255,255,0.55)" strokeWidth={4} />
            <line x1={70} y1={150} x2={130} y2={150} stroke="rgba(255,255,255,0.8)" strokeWidth={4} strokeDasharray="6 5" />
          </svg>
          <div style={{ position: "absolute", right: -10, top: 40, width: 66, height: 66, borderRadius: "50%",
                        background: "#22C55E", color: "#FFFFFF", fontWeight: 900, fontSize: 38, display: "flex",
                        alignItems: "center", justifyContent: "center", border: "4px solid #FFFFFF",
                        scale: interpolate(tick, [0, 1], [0, 1]) }}>✓</div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8, opacity: Math.min(1, lab * 1.5),
                      translate: `${interpolate(lab, [0, 1], [40, 0])}px 0px` }}>
          <div style={{ padding: "10px 22px", borderRadius: 18, background: PALETTE.plumCard, color: PALETTE.cardText,
                        fontWeight: 900, fontSize: 50, lineHeight: 1.08, textTransform: "uppercase",
                        boxShadow: "0 14px 30px rgba(0,0,0,0.3)" }}>
            <Rich text={item.label || "VỪA *LAPTOP*"} />
          </div>
          {item.sub ? (
            <div style={{ alignSelf: "flex-start", padding: "6px 18px", borderRadius: 14, background: "rgba(20, 18, 24, 0.82)",
                          color: "#FFFFFF", fontWeight: 700, fontSize: 32 }}>{plainText(item.sub)}</div>
          ) : null}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Checklist ngăn: tiêu đề `label` ("BÊN TRONG CÓ GÌ"), mỗi dòng `steps` "TÊN NGĂN | ghi chú"; dòng hiện + được tích
 *  đúng lúc nói (`times`, giây từ đầu thẻ; thiếu thì chia đều). Tối đa 5 dòng. */
export const CompartmentsFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const fade = useFade();
  const rows = (item.steps ?? []).slice(0, 5).map((s) => {
    const [title, sub] = s.split("|").map((x) => x.trim());
    return { title, sub };
  });
  const per = Math.max(1, (durationInFrames - FADE * 2) / Math.max(1, rows.length));
  const times = item.times ?? [];
  const at = rows.map((_, i) => (times.length > i ? Math.round(times[i] * fps) : FADE + Math.round(i * per)));
  const head = spring({ frame, fps, config: { damping: 14, stiffness: 190 } });
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div style={{ position: "absolute", top: `${(item.y ?? 0.2) * 100}%`, width: 600, display: "flex",
                    flexDirection: "column", gap: 10, padding: "16px 20px", borderRadius: 26, fontFamily: FONT_STACK,
                    background: PALETTE.plumCard, boxShadow: "0 16px 34px rgba(0,0,0,0.35)",
                    opacity: Math.min(1, head * 1.5), scale: interpolate(head, [0, 1], [0.9, 1]) }}>
        <div style={{ fontWeight: 900, fontSize: 40, color: PALETTE.pink, textTransform: "uppercase", letterSpacing: "0.03em" }}>
          <Rich text={item.label || "BÊN TRONG CÓ GÌ"} />
        </div>
        {rows.map((r, i) => {
          const p = spring({ frame: frame - at[i], fps, config: { damping: 15, stiffness: 200 } });
          const t = spring({ frame: frame - at[i] - 6, fps, config: { damping: 9, stiffness: 260 } });
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 14, opacity: Math.min(1, p * 1.5),
                                  translate: `${interpolate(p, [0, 1], [-40, 0])}px 0px` }}>
              <div style={{ width: 46, height: 46, flex: "0 0 46px", borderRadius: 12, border: `3px solid ${PALETTE.pink}`,
                            display: "flex", alignItems: "center", justifyContent: "center", color: "#FFFFFF",
                            background: t > 0.05 ? "#22C55E" : "transparent", fontWeight: 900, fontSize: 30 }}>
                <span style={{ scale: interpolate(t, [0, 1], [0, 1]) }}>✓</span>
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: 12, minWidth: 0 }}>
                <div style={{ fontWeight: 900, fontSize: 38, color: PALETTE.cardText, textTransform: "uppercase",
                              whiteSpace: "nowrap" }}>{plainText(r.title)}</div>
                {r.sub ? <div style={{ fontWeight: 700, fontSize: 28, color: PALETTE.cardText, opacity: 0.8,
                                       whiteSpace: "nowrap" }}>{plainText(r.sub)}</div> : null}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const ICONS: Record<string, (c: string) => React.ReactElement> = {
  // giọt nước + ô: chống nước
  water: (c) => <path d="M50 14 C50 14 24 46 24 62 A26 26 0 0 0 76 62 C76 46 50 14 50 14 Z" fill={c} />,
  // ô vải đan chéo: chất liệu
  material: (c) => (
    <g stroke={c} strokeWidth={7} fill="none">
      <rect x={20} y={20} width={60} height={60} rx={10} />
      <path d="M20 40 L60 80 M20 60 L40 80 M40 20 L80 60 M60 20 L80 40" />
    </g>
  ),
  // quả tạ: nhẹ
  weight: (c) => (
    <g fill={c}>
      <path d="M30 40 L70 40 L80 82 L20 82 Z" />
      <circle cx={50} cy={30} r={11} fill="none" stroke={c} strokeWidth={7} />
    </g>
  ),
  // khoá kéo
  zip: (c) => (
    <g stroke={c} strokeWidth={7} fill="none" strokeLinecap="round">
      <path d="M50 12 L50 88" />
      <path d="M40 22 L60 22 M40 36 L60 36 M40 50 L60 50" />
      <rect x={38} y={58} width={24} height={26} rx={6} fill={c} />
    </g>
  ),
  // khiên: bảo hành
  warranty: (c) => <path d="M50 12 L82 24 L82 50 C82 70 68 84 50 90 C32 84 18 70 18 50 L18 24 Z" fill={c} />,
  star: (c) => <path d="M50 10 L61 38 L90 38 L66 56 L75 86 L50 68 L25 86 L34 56 L10 38 L39 38 Z" fill={c} />,
};

/** Huy hiệu tính năng/chất liệu: vòng tròn icon (`icon`) bật vào + xoay nhẹ, nhãn `label` ("CHỐNG NƯỚC"),
 *  dòng phụ `sub` ("vải Oxford 900D"). */
export const BadgeFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useFade();
  const pop = spring({ frame, fps, config: { damping: 9, stiffness: 220 } });
  const lab = spring({ frame: frame - 8, fps, config: { damping: 13, stiffness: 200 } });
  const wobble = 4 * Math.sin((frame / fps) * Math.PI * 1.2);
  const icon = ICONS[item.icon ?? ""] ?? ICONS.star;
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div style={{ position: "absolute", top: `${(item.y ?? 0.45) * 100}%`, width: 560, display: "flex",
                    alignItems: "center", gap: 18, fontFamily: FONT_STACK }}>
        <div style={{ width: 170, height: 170, flex: "0 0 170px", borderRadius: "50%", background: PALETTE.plumCard,
                      border: `6px solid ${PALETTE.pink}`, display: "flex", alignItems: "center", justifyContent: "center",
                      boxShadow: "0 14px 30px rgba(0,0,0,0.35)", scale: interpolate(pop, [0, 1], [0.3, 1]),
                      rotate: `${interpolate(pop, [0, 1], [-30, 0]) + wobble}deg` }}>
          <svg width={100} height={100} viewBox="0 0 100 100">{icon(PALETTE.pink)}</svg>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8, opacity: Math.min(1, lab * 1.5),
                      translate: `${interpolate(lab, [0, 1], [40, 0])}px 0px` }}>
          <div style={{ padding: "10px 22px", borderRadius: 18, background: PALETTE.plumCard, color: PALETTE.cardText,
                        fontWeight: 900, fontSize: 48, lineHeight: 1.08, textTransform: "uppercase",
                        boxShadow: "0 14px 30px rgba(0,0,0,0.3)" }}>
            <Rich text={item.label || "*CHỐNG NƯỚC*"} />
          </div>
          {item.sub ? (
            <div style={{ alignSelf: "flex-start", padding: "6px 18px", borderRadius: 14, background: "rgba(20, 18, 24, 0.82)",
                          color: "#FFFFFF", fontWeight: 700, fontSize: 30 }}>{plainText(item.sub)}</div>
          ) : null}
        </div>
      </div>
    </AbsoluteFill>
  );
};
