import {
  AbsoluteFill,
  Easing,
  Img,
  staticFile,
  interpolate,
  interpolateColors,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { BRAND, FONT_STACK, GraphicItem, OverlayItem, PALETTE, Safe, parseRich, plainText, safeCenteredW } from "./types";

const LIGHT = {
  blue: { solid: "#2F7BFF", glow: "47, 123, 255" },
  red: { solid: "#FF3B4E", glow: "255, 59, 78" },
};
const FADE = 8;

const useFade = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return interpolate(frame, [0, FADE, durationInFrames - FADE, durationInFrames], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
};

/** Đèn xanh/đỏ: viền sáng màu nhịp thở quanh khung + hạt sáng bay lên + thẻ đồng hồ đếm phút. */
export const LightFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const fade = useFade();
  const c = LIGHT[item.color];
  const breathe = 0.75 + 0.25 * Math.sin((frame / fps) * Math.PI * 1.6);
  const enter = spring({ frame, fps, config: { damping: 14, stiffness: 160 } });
  const progress = interpolate(frame, [FADE, durationInFrames - FADE], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const R = 46;
  const C = 2 * Math.PI * R;

  return (
    <AbsoluteFill style={{ opacity: fade }}>
      {/* vầng sáng quanh mép khung, giữa khung để trống cho mặt/sản phẩm */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse 75% 60% at 50% 50%, transparent 55%, rgba(${c.glow}, ${0.42 * breathe}) 100%)`,
          boxShadow: `inset 0 0 160px 30px rgba(${c.glow}, ${0.55 * breathe})`,
        }}
      />
      {/* hạt sáng dọc hai mép */}
      {Array.from({ length: 10 }).map((_, i) => {
        const side = i % 2 === 0 ? 40 + (i * 7) % 60 : 1080 - 40 - (i * 11) % 60;
        const speed = 160 + (i * 37) % 120;
        const y = 1920 - (((frame + i * 23) * speed) / fps) % 2100;
        const size = 10 + (i * 5) % 14;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: side,
              top: y,
              width: size,
              height: size,
              borderRadius: "50%",
              // hạt trang trí chạy dọc mép (ngoài vùng an toàn): giữ mờ < 85 % để không thành "vật thể đặc"
              background: `rgba(${c.glow}, 0.7)`,
              boxShadow: `0 0 ${size * 2}px ${size}px rgba(${c.glow}, 0.45)`,
            }}
          />
        );
      })}
      {/* thẻ đồng hồ — chỉ khi có nhãn (nguồn đã có chữ in sẵn thì bỏ, tránh vòng tròn trơ trọi đè lên mặt) */}
      {item.label && <div
        style={{
          position: "absolute",
          top: `${(item.y ?? 0.1) * 100}%`,
          left: "50%",
          translate: `-50% ${interpolate(enter, [0, 1], [-40, 0])}px`,
          scale: interpolate(enter, [0, 1], [0.85, 1]),
          height: 150,
          display: "flex",
          alignItems: "center",
          gap: 26,
          padding: "0 40px 0 22px",
          borderRadius: 75,
          background: "rgba(10, 12, 20, 0.72)",
          border: `3px solid rgba(${c.glow}, 0.9)`,
          boxShadow: `0 0 40px rgba(${c.glow}, 0.55)`,
        }}
      >
        <svg width={112} height={112} viewBox="0 0 112 112">
          <circle cx={56} cy={56} r={R} fill="none" stroke="rgba(255,255,255,0.18)" strokeWidth={10} />
          <circle
            cx={56}
            cy={56}
            r={R}
            fill="none"
            stroke={c.solid}
            strokeWidth={10}
            strokeLinecap="round"
            strokeDasharray={C}
            strokeDashoffset={C * (1 - progress)}
            transform="rotate(-90 56 56)"
          />
          <circle cx={56} cy={56} r={18 + 4 * breathe} fill={c.solid} style={{ filter: `drop-shadow(0 0 12px ${c.solid})` }} />
        </svg>
        <div style={{ fontFamily: FONT_STACK, fontWeight: 900, fontSize: 54, color: "#FFFFFF", whiteSpace: "nowrap" }}>
          {item.label}
        </div>
      </div>}
    </AbsoluteFill>
  );
};

const TOOTH =
  "M40,30 C40,8 80,4 100,20 C120,4 160,8 160,30 C170,80 150,110 145,150 C140,205 122,218 114,182 " +
  "C109,160 91,160 86,182 C78,218 60,205 55,150 C50,110 30,80 40,30 Z";

const Sparkle: React.FC<{ x: number; y: number; s: number; delay: number }> = ({ x, y, s, delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - delay, fps, config: { damping: 10, stiffness: 200 } });
  const twinkle = 0.8 + 0.2 * Math.sin((frame - delay) / 3);
  return (
    <path
      d={`M${x},${y - s} L${x + s * 0.25},${y - s * 0.25} L${x + s},${y} L${x + s * 0.25},${y + s * 0.25} ` +
        `L${x},${y + s} L${x - s * 0.25},${y + s * 0.25} L${x - s},${y} L${x - s * 0.25},${y - s * 0.25} Z`}
      fill="#FFFFFF"
      stroke="#9AD7FF"
      strokeWidth={2}
      style={{ transformOrigin: `${x}px ${y}px`, scale: `${p * twinkle}` }}
    />
  );
};

/** Icon răng ngả vàng → trắng, nhãn "Trước"/"Sau", thanh màu răng. Ghi rõ "Hình minh họa" (không phải ảnh thật). */
export const WhitenFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const fade = useFade();
  const enter = spring({ frame, fps, config: { damping: 13, stiffness: 170 } });
  const t = interpolate(frame, [durationInFrames * 0.2, durationInFrames * 0.65], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.45, 0, 0.25, 1),
  });
  const fill = interpolateColors(t, [0, 1], ["#E2BE5E", "#FFFFFF"]);
  const sparkleAt = Math.round(durationInFrames * 0.62);

  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div
        style={{
          position: "absolute",
          top: `${(item.y ?? 0.1) * 100}%`,
          width: 520,
          height: 520,
          borderRadius: 40,
          background: "rgba(255, 255, 255, 0.9)",
          boxShadow: "0 24px 60px rgba(0,0,0,0.35)",
          scale: interpolate(enter, [0, 1], [0.7, 1]),
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          fontFamily: FONT_STACK,
          fontWeight: 900,
        }}
      >
        <div style={{ position: "relative", height: 84, width: "100%", marginTop: 22 }}>
          {(["Trước", "Sau"] as const).map((label, i) => (
            <div
              key={label}
              style={{
                position: "absolute",
                inset: 0,
                textAlign: "center",
                fontSize: 60,
                color: i === 0 ? "#8A6A1E" : "#1F6FFF",
                opacity: i === 0 ? 1 - t : t,
              }}
            >
              {label}
            </div>
          ))}
        </div>
        <svg width={300} height={300} viewBox="0 0 200 230">
          <path d={TOOTH} fill={fill} stroke="#3A3A3A" strokeWidth={5} strokeLinejoin="round" />
          <path d="M62,44 C70,30 88,30 94,40" fill="none" stroke="rgba(255,255,255,0.85)" strokeWidth={7} strokeLinecap="round" />
          {frame >= sparkleAt && (
            <>
              <Sparkle x={168} y={34} s={20} delay={sparkleAt} />
              <Sparkle x={30} y={70} s={14} delay={sparkleAt + 4} />
              <Sparkle x={160} y={120} s={11} delay={sparkleAt + 8} />
            </>
          )}
        </svg>
        <div
          style={{
            width: 400,
            height: 22,
            borderRadius: 11,
            marginTop: 8,
            background: "linear-gradient(90deg, #D9B04A, #F3E3B0, #FFFFFF)",
            border: "2px solid rgba(0,0,0,0.15)",
            position: "relative",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: -9,
              left: `calc(${t * 100}% - 18px)`,
              width: 36,
              height: 36,
              borderRadius: "50%",
              background: "#1F6FFF",
              border: "5px solid #FFFFFF",
              boxShadow: "0 3px 8px rgba(0,0,0,0.35)",
            }}
          />
        </div>
        <div style={{ marginTop: 16, fontSize: 26, fontWeight: 600, color: "#666666" }}>Hình minh họa</div>
      </div>
    </AbsoluteFill>
  );
};

const YELLOW = "#D8B24A";
const WHITE = "#FFFFFF";
// 6 răng hàm trên + 6 răng hàm dưới (x, rộng, cao) trong viewBox 560x300
const UPPER = [
  [118, 52, 66], [172, 56, 78], [230, 58, 88], [290, 58, 88], [350, 56, 78], [408, 52, 66],
];
const LOWER = [
  [140, 48, 52], [190, 50, 58], [242, 52, 62], [296, 52, 62], [348, 50, 58], [398, 48, 52],
];

/** Hàm răng vector: pha xanh — thanh LED quét, răng vàng → trắng lần lượt; pha đỏ — nướu dịu lại, răng lấp lánh.
 *  Ghi "Minh họa" (đồ hoạ, không phải kết quả thật). */
export const TeethFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const fade = useFade();
  const enter = spring({ frame, fps, config: { damping: 13, stiffness: 170 } });
  const splitF = Math.round(durationInFrames * (item.split ?? 0.56));
  // split = 1: chỉ pha xanh; răng trắng xong ở 80 % thời lượng rồi lấp lánh
  const blueEnd = Math.max(FADE + 1, Math.min(splitF, Math.round(durationInFrames * 0.8)));
  const blue = interpolate(frame, [FADE, blueEnd], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // không có pha đỏ (split ≈ 1) thì khoảng [splitF, cuối] rỗng → red = 0
  const red = splitF < durationInFrames - FADE - 1
    ? interpolate(frame, [splitF, durationInFrames - FADE], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 0;
  const inRed = frame >= splitF;
  const phase = inRed ? LIGHT.red : LIGHT.blue;
  const pulse = 0.7 + 0.3 * Math.sin((frame / fps) * Math.PI * 2.4);
  // thanh LED quét trái → phải trong pha xanh
  const sweepX = interpolate(blue, [0, 1], [70, 490]);

  const toothFill = (x: number, w: number) => {
    const center = x + w / 2;
    // răng trắng dần khi thanh sáng đã quét qua
    const p = interpolate(sweepX - center, [-20, 60], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    return interpolateColors(Math.max(p, inRed ? 1 : 0), [0, 1], [YELLOW, WHITE]);
  };

  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div
        style={{
          position: "absolute",
          top: `${(item.y ?? 0.08) * 100}%`,
          width: 540,
          height: 350,
          borderRadius: 40,
          background: PALETTE.plumCard,
          border: `4px solid rgba(${phase.glow}, ${0.6 + 0.4 * pulse})`,
          boxShadow: `0 0 ${50 * pulse}px rgba(${phase.glow}, 0.65), 0 20px 50px rgba(0,0,0,0.45)`,
          scale: interpolate(enter, [0, 1], [0.75, 1]),
          overflow: "hidden",
        }}
      >
        <svg width={540} height={350} viewBox="-30 -50 620 400">
          <defs>
            <linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stopColor={phase.solid} stopOpacity="0" />
              <stop offset="0.5" stopColor={phase.solid} stopOpacity="0.85" />
              <stop offset="1" stopColor={phase.solid} stopOpacity="0" />
            </linearGradient>
            <radialGradient id="gumGlow">
              <stop offset="0" stopColor="#FF4D5E" stopOpacity={0.75 * red * pulse} />
              <stop offset="1" stopColor="#FF4D5E" stopOpacity="0" />
            </radialGradient>
            <clipPath id="mouth">
              <path d="M70,40 C170,-10 390,-10 490,40 C480,190 380,250 280,250 C180,250 80,190 70,40 Z" />
            </clipPath>
          </defs>
          {/* môi */}
          <path d="M40,40 C160,-40 400,-40 520,40 C510,230 390,290 280,290 C170,290 50,230 40,40 Z" fill="#E7708E" />
          {/* lòng miệng */}
          <path d="M70,40 C170,-10 390,-10 490,40 C480,190 380,250 280,250 C180,250 80,190 70,40 Z" fill="#4A1624" />
          <g clipPath="url(#mouth)">
            {/* nướu trên/dưới — đỏ ửng rồi dịu lại ở pha đỏ */}
            <path d="M60,0 L500,0 L500,34 C400,20 160,20 60,34 Z" fill={interpolateColors(red, [0, 1], ["#F39AAA", "#F7B6C2"])} />
            <path d="M60,250 L500,250 L500,200 C400,214 160,214 60,200 Z" fill={interpolateColors(red, [0, 1], ["#F39AAA", "#F7B6C2"])} />
            <ellipse cx={280} cy={30} rx={260} ry={60} fill="url(#gumGlow)" />
            <ellipse cx={280} cy={215} rx={240} ry={50} fill="url(#gumGlow)" />
            {UPPER.map(([x, w, h], i) => (
              <rect key={`u${i}`} x={x} y={22} width={w} height={h} rx={16} fill={toothFill(x, w)} stroke="#B98F7A" strokeWidth={2} />
            ))}
            {LOWER.map(([x, w, h], i) => (
              <rect key={`l${i}`} x={x} y={212 - h} width={w} height={h} rx={14} fill={toothFill(x, w)} stroke="#B98F7A" strokeWidth={2} />
            ))}
            {/* thanh LED quét (pha xanh), phủ cả hàm (pha đỏ) */}
            {!inRed ? (
              <rect x={sweepX - 70} y={0} width={140} height={260} fill="url(#beam)" style={{ mixBlendMode: "screen" }} />
            ) : null}
          </g>
          {/* răng lấp lánh khi đã trắng */}
          {frame >= blueEnd && (
            <>
              <Sparkle x={150} y={50} s={22} delay={blueEnd} />
              <Sparkle x={395} y={60} s={18} delay={blueEnd + 5} />
              <Sparkle x={280} y={180} s={14} delay={blueEnd + 10} />
            </>
          )}
        </svg>
        {/* chấm màu pha đèn + nhãn nhỏ bắt buộc */}
        <div
          style={{
            position: "absolute",
            left: 26,
            top: 22,
            width: 30,
            height: 30,
            borderRadius: "50%",
            background: phase.solid,
            boxShadow: `0 0 ${18 * pulse}px ${phase.solid}`,
          }}
        />
        <div
          style={{
            position: "absolute",
            right: 22,
            bottom: 14,
            fontFamily: FONT_STACK,
            fontWeight: 700,
            fontSize: 24,
            color: "rgba(255,255,255,0.7)",
          }}
        >
          Minh họa
        </div>
      </div>
    </AbsoluteFill>
  );
};


/** Thẻ toàn màn hình đếm ngày (style guide mục 5: bộ đếm kiểu B + thẻ chuyển ý kiểu A): "NGÀY 1 → 7". */
export const CounterFx: React.FC<{ item: GraphicItem; safe: Safe }> = ({ item }) => {
  // feedback lo-04: thẻ gọn nổi trên video đang chạy (trước là thẻ toàn màn hình → ngắt quãng, cắt người nói)
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const fade = useFade();
  const enter = spring({ frame, fps, config: { damping: 14, stiffness: 190, overshootClamping: true } });
  const p = interpolate(frame, [4, durationInFrames - 8], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.3, 0, 0.2, 1),
  });
  const n = Math.max(2, item.days || 7); // đếm NGÀY 1 → n (mặc định 7; theo đúng số ngày người nói nói ra)
  const day = Math.max(1, Math.min(n, 1 + Math.floor(p * n)));
  const bump = spring({ frame: frame - Math.round((day - 1) / n * (durationInFrames - 12)) - 4, fps,
                        config: { damping: 10, stiffness: 260 } });
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div style={{ position: "absolute", top: `${(item.y ?? 0.13) * 100}%`, width: 520, height: 200, boxSizing: "border-box",
                    borderRadius: 32, background: PALETTE.plumCard, boxShadow: "0 20px 50px rgba(0,0,0,0.4)",
                    display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                    fontFamily: FONT_STACK, fontWeight: 900, scale: interpolate(enter, [0, 1], [0.85, 1]) }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 18 }}>
          <span style={{ color: PALETTE.cardText, fontSize: 40, letterSpacing: "0.1em" }}>NGÀY</span>
          <span style={{ color: PALETTE.pink, fontSize: 96, lineHeight: 1, display: "inline-block",
                         scale: interpolate(bump, [0, 1], [1.2, 1]) }}>{day}</span>
        </div>
        <div style={{ display: "flex", gap: 14, marginTop: 10 }}>
          {Array.from({ length: n }).map((_, i) => (
            <div key={i} style={{ width: 20, height: 20, borderRadius: "50%",
                                  background: i < day ? PALETTE.pink : "rgba(255,255,255,0.2)",
                                  boxShadow: i < day ? `0 0 12px ${PALETTE.pink}` : "none" }} />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};


// ───────────── Phong cách Vox: bút dạ vàng, khoanh tay, giấy dán ─────────────

/** Nhãn bút dạ: chữ đen đậm, vệt vàng quét từ trái sang, nghiêng nhẹ. */
const Highlight: React.FC<{ text: string; fontSize: number; delay?: number; rotate?: number; maxWidth?: number }> = ({
  text,
  fontSize,
  delay = 0,
  rotate = -2,
  maxWidth = 816,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sweep = interpolate(frame - delay, [0, 0.3 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.6, 0, 0.3, 1),
  });
  const textIn = interpolate(frame - delay, [0.12 * fps, 0.28 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <span
      style={{
        display: "inline-block",
        rotate: `${rotate}deg`,
        padding: "6px 22px 10px",
        fontFamily: FONT_STACK,
        fontWeight: 900,
        fontSize,
        lineHeight: 1.1,
        color: `rgba(17,17,17,${textIn})`,
        textTransform: "uppercase",
        backgroundImage: `linear-gradient(100deg, ${PALETTE.marker} 0%, ${PALETTE.marker} 96%, transparent 100%)`,
        backgroundSize: `${sweep * 100}% 86%`,
        backgroundPosition: "0 60%",
        backgroundRepeat: "no-repeat",
        // xuống dòng trong bề rộng an toàn thay vì tràn ra mép (vệt bút dạ tô theo từng dòng)
        maxWidth,
        boxSizing: "border-box",
        textWrap: "balance",
        boxDecorationBreak: "clone",
        WebkitBoxDecorationBreak: "clone",
      }}
    >
      {text}
    </span>
  );
};

/** Chữ kiểu Vox: dòng chính trên vệt bút dạ vàng, dòng phụ trên dải giấy trắng. */
export const VoxLabel: React.FC<{ item: OverlayItem; safe: Safe }> = ({ item, safe }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const exit = interpolate(frame, [durationInFrames - 6, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const subIn = interpolate(frame, [10, 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ alignItems: "center", opacity: exit }}>
      <div style={{ position: "absolute", top: `${(item.y ?? 0.5) * 100}%`, textAlign: "center",
                    maxWidth: item.max_w ?? safeCenteredW(safe) }}>
        <Highlight text={plainText(item.text)} fontSize={58} maxWidth={item.max_w ?? safeCenteredW(safe)} />
        {item.sub ? (
          <div style={{ marginTop: 10 }}>
            <span
              style={{
                display: "inline-block",
                rotate: "1deg",
                padding: "6px 16px",
                background: "#FFFFFF",
                fontFamily: FONT_STACK,
                fontWeight: 700,
                fontSize: 36,
                color: "#111111",
                opacity: subIn,
              }}
            >
              {item.sub}
            </span>
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

/** Đường vòng khoanh vẽ tay: vượt quá một vòng một chút, bán kính rung nhẹ. */
const handEllipse = (cx: number, cy: number, rx: number, ry: number, wob: number) => {
  const pts: string[] = [];
  for (let i = 0; i <= 40; i++) {
    const a = (i / 40) * Math.PI * 2.12 - 0.4;
    const r = 1 + wob * Math.sin(i * 1.7);
    pts.push(`${(cx + rx * r * Math.cos(a)).toFixed(1)},${(cy + ry * r * Math.sin(a)).toFixed(1)}`);
  }
  return `M${pts.join(" L")}`;
};

/** Vox callout: khoanh đỏ vẽ tay quanh vùng (cx, cy, rx, ry) → mũi tên → nhãn bút dạ bên dưới. */
export const CalloutFx: React.FC<{ item: GraphicItem; safe: Safe }> = ({ item, safe }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const W = 1080;
  const H = 1920;
  const cx = (item.cx ?? 0.5) * W;
  const cy = (item.cy ?? 0.5) * H;
  const rx = (item.rx ?? 0.25) * W;
  const ry = (item.ry ?? 0.08) * H;
  const t0 = Math.round(0.22 * fps); // chờ zoom ống kính gần xong
  const draw = interpolate(frame, [t0, t0 + 0.3 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });
  const arrow = interpolate(frame, [t0 + 0.25 * fps, t0 + 0.42 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exit = interpolate(frame, [durationInFrames - 5, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // nhãn dưới vòng khoanh; không đủ chỗ trong vùng an toàn thì đặt lên trên vòng
  const LABEL_H = 100;
  const below = cy + ry + 0.1 * H;
  const above = cy - ry - 0.1 * H - LABEL_H;
  // `y` > 0: mép trên nhãn đặt tay (lo-05: nhãn trên vòng rơi đúng mặt người → đưa lên trên đầu, mũi tên dài)
  const fixedY = (item.y ?? 0) > 0 ? (item.y as number) * H : null;
  const labelBelow = fixedY !== null ? fixedY > cy : below + LABEL_H <= H - safe.bottom || above < safe.top;
  const labelY = Math.max(safe.top, Math.min(fixedY ?? (labelBelow ? below : above), H - safe.bottom - LABEL_H));
  const L = 2600;
  const ax0 = Math.min(cx + 0.18 * W, W - safe.rail_w - 20);
  const ay0 = labelBelow ? labelY - 10 : labelY + LABEL_H + 10;
  const ax1 = cx + rx * 0.55;
  const ay1 = labelBelow ? cy + ry * 0.95 : cy - ry * 0.95;
  return (
    <AbsoluteFill style={{ opacity: exit }}>
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        {[0, 1].map((k) => (
          <path
            key={k}
            d={handEllipse(cx + k * 4, cy - k * 3, rx * (1 + k * 0.03), ry * (1 - k * 0.04), 0.035)}
            fill="none"
            stroke={PALETTE.ink}
            strokeWidth={k ? 6 : 11}
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray={L}
            strokeDashoffset={L * (1 - draw)}
            opacity={k ? 0.75 : 1}
            style={{ filter: "drop-shadow(0 2px 3px rgba(0,0,0,0.35))" }}
          />
        ))}
        {item.label ? (
          <>
            <path
              d={`M${ax0},${ay0} Q${ax0 + 40},${(ay0 + ay1) / 2} ${ax1},${ay1}`}
              fill="none"
              stroke={PALETTE.ink}
              strokeWidth={9}
              strokeLinecap="round"
              strokeDasharray={600}
              strokeDashoffset={600 * (1 - arrow)}
            />
            {arrow >= 1 && (
              <path
                d={labelBelow ? `M${ax1 - 30},${ay1 + 22} L${ax1},${ay1} L${ax1 + 26},${ay1 + 30}`
                  : `M${ax1 - 30},${ay1 - 22} L${ax1},${ay1} L${ax1 + 26},${ay1 - 30}`}
                fill="none"
                stroke={PALETTE.ink}
                strokeWidth={9}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            )}
          </>
        ) : null}
      </svg>
      {item.label ? (
        <div style={{ position: "absolute", top: labelY, left: safe.side,
                      right: labelY + LABEL_H > safe.rail_top ? safe.rail_w : safe.side, textAlign: "center" }}>
          <Highlight text={plainText(item.label)} fontSize={70} delay={t0 + Math.round(0.35 * fps)}
                     maxWidth={W - safe.side - (labelY + LABEL_H > safe.rail_top ? safe.rail_w : safe.side) - 24} />
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

/** Vox collage: nền giấy có hạt, các ảnh (cắt từ nguồn) dán băng keo, nghiêng, nhãn bút dạ. */
export const CollageFx: React.FC<{ item: GraphicItem; safe: Safe }> = ({ item, safe }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const stills = item.stills ?? [];
  const fade = interpolate(frame, [0, 4, durationInFrames - 5, durationInFrames], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  // feedback lo-03: ảnh ghép là thẻ toàn màn hình nền kín → bỏ qua vùng an toàn; ảnh to, giãn ra, không chồng nhau
  // (ảnh 1 nửa trên, ảnh 2 nửa dưới, mỗi ảnh ≤ 900x640, nhãn bút dạ dưới mỗi ảnh không bị ảnh kia che)
  const IMG_W = 900;
  const IMG_H = 640;
  void safe;
  const layout = stills.length === 1
    ? [{ top: 560, left: Math.round((1080 - IMG_W - 32) / 2), rot: -3 }]
    : [
        { top: 90, left: 50, rot: -3 },
        { top: 1000, left: 110, rot: 3 },
      ];
  return (
    <AbsoluteFill style={{ opacity: fade, background: PALETTE.paper }}>
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, opacity: 0.35, mixBlendMode: "multiply" }}>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={3} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#grain)" />
      </svg>
      {stills.slice(0, 2).map((st, i) => {
        const at = Math.round(i * 0.45 * fps);
        const p = spring({ frame: frame - at, fps, config: { damping: 14, stiffness: 150 } });
        const L = layout[i];
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              top: L.top,
              left: L.left,
              rotate: `${L.rot}deg`,
              translate: `0px ${interpolate(p, [0, 1], [120, 0])}px`,
              opacity: Math.min(1, p * 1.5),
            }}
          >
            <div style={{ background: "#FFFFFF", padding: 16, paddingBottom: 18, boxShadow: "0 18px 36px rgba(0,0,0,0.28)" }}>
              <Img src={staticFile(st.file)} style={{ maxWidth: IMG_W, maxHeight: IMG_H, display: "block" }} />
            </div>
            <div
              style={{
                position: "absolute",
                top: -26,
                left: "40%",
                width: 170,
                height: 52,
                rotate: `${-L.rot * 1.6}deg`,
                background: "rgba(240, 228, 196, 0.85)",
                boxShadow: "0 2px 4px rgba(0,0,0,0.12)",
              }}
            />
            {st.label ? (
              <div style={{ position: "absolute", bottom: -64, left: i ? "auto" : 10, right: i ? 10 : "auto" }}>
                <Highlight text={plainText(st.label)} fontSize={68} delay={at + Math.round(0.25 * fps)} rotate={i ? 2 : -3} />
              </div>
            ) : null}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};


/** Thang màu răng: các ô màu từ trắng (1) tới vàng (n), con trỏ trượt from_shade → to_shade.
 *  Chỉ dùng số người nói nói ra; nhãn ghi nguồn ("theo trải nghiệm của …"). Thẻ nằm gọn trong vùng an toàn. */
export const ShadeFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const fade = useFade();
  const enter = spring({ frame, fps, config: { damping: 14, stiffness: 170 } });
  const from = item.from_shade ?? 10;
  const to = item.to_shade ?? 5;
  const n = Math.max(10, from, to);
  const move = interpolate(frame, [0.35 * fps, Math.max(0.35 * fps + 1, durationInFrames * 0.7)], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.45, 0, 0.2, 1),
  });
  const W = 620; // khớp vf/placement.py GRAPHIC_W_PX["shade"] (vừa khoảng an toàn ở hàng cột nút)
  const cell = (W - 60) / n;
  const pos = from + (to - from) * move; // mức hiện tại (số thực)
  const px = 30 + (pos - 0.5) * cell;
  const shown = Math.round(pos);
  // days > 0: nhãn NGÀY 1 → days chạy cùng con trỏ (thang đo độ trắng theo ngày — gợi ý người dùng sau lo-03)
  const days = item.days ?? 0;
  const day = days > 0 ? Math.max(1, Math.min(days, 1 + Math.round(move * (days - 1)))) : 0;
  const dayBump = days > 0 ? spring({ frame: frame - Math.round(0.35 * fps + ((day - 1) / Math.max(1, days - 1)) * (durationInFrames * 0.7 - 0.35 * fps)), fps,
                                      config: { damping: 10, stiffness: 260 } }) : 1;
  const swatch = (i: number) => interpolateColors(i, [1, n], ["#FFFFFF", "#D9AE52"]);
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div
        style={{
          position: "absolute",
          top: `${(item.y ?? 0.15) * 100}%`,
          width: W,
          height: 300,
          boxSizing: "border-box",
          borderRadius: 32,
          background: PALETTE.plumCard,
          boxShadow: "0 20px 50px rgba(0,0,0,0.4)",
          scale: interpolate(enter, [0, 1], [0.8, 1]),
          fontFamily: FONT_STACK,
          fontWeight: 900,
          color: PALETTE.cardText  // preset reply: thẻ trắng chữ mực (lo-06),
        }}
      >
        <div style={{ position: "absolute", top: 24, left: 30, fontSize: 30, letterSpacing: "0.04em", whiteSpace: "nowrap" }}>THANG MÀU RĂNG</div>
        {days > 0 ? (
          <div style={{ position: "absolute", top: 18, left: 360, padding: "4px 16px", borderRadius: 999, fontSize: 32,
                        background: PALETTE.keyBox, color: "#FFFFFF", scale: interpolate(dayBump, [0, 1], [1.3, 1]) }}>
            NGÀY {day}
          </div>
        ) : null}
        <div style={{ position: "absolute", top: 14, right: 30, fontSize: 64, color: PALETTE.pink }}>{shown}</div>
        <div style={{ position: "absolute", top: 120, left: 30, display: "flex" }}>
          {Array.from({ length: n }).map((_, i) => (
            <div key={i} style={{ width: cell - 4, marginRight: 4, height: 70, borderRadius: 10, background: swatch(i + 1),
                                  border: "2px solid rgba(0,0,0,0.15)", boxSizing: "border-box", display: "flex",
                                  alignItems: "flex-end", justifyContent: "center", fontSize: 20, color: "#5B4630" }}>
              {i + 1}
            </div>
          ))}
        </div>
        {/* con trỏ */}
        <div style={{ position: "absolute", top: 86, left: px - 18, width: 0, height: 0,
                      borderLeft: "18px solid transparent", borderRight: "18px solid transparent",
                      borderTop: `26px solid ${PALETTE.pink}` }} />
        {item.label ? (
          <div style={{ position: "absolute", bottom: 22, left: 30, right: 30, fontSize: 28, fontWeight: 700,
                        color: "rgba(255,255,255,0.85)" }}>{item.label}</div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

/** Thanh gạt trước/sau: 2 ảnh cắt từ nguồn chồng nhau trong khung an toàn, vạch dọc quét trái → phải lộ ảnh "sau". */
export const WipeFx: React.FC<{ item: GraphicItem; safe: Safe }> = ({ item }) => {
  // feedback lo-04: khung nhỏ trên nền tím → thẻ lớn rộng ~1000 px nổi trên video (người nói vẫn chạy quanh thẻ),
  // giữ tỉ lệ ảnh, zoom chậm 1 → 1,04; vạch gạt quét lộ ảnh "sau". Thẻ so sánh lớn được bỏ qua vùng an toàn.
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const stills = item.stills ?? [];
  const fade = interpolate(frame, [0, 6, durationInFrames - 6, durationInFrames], [0, 1, 1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const enter = spring({ frame, fps, config: { damping: 16, stiffness: 170, overshootClamping: true } });
  const sweep = interpolate(frame, [0.4 * fps, Math.max(0.4 * fps + 1, durationInFrames * 0.6)], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.65, 0, 0.35, 1),
  });
  const kb = interpolate(frame, [0, durationInFrames], [1, 1.04]);
  const BW = 1000;
  const before = stills[0];
  const after = stills[1] ?? stills[0];
  const img: React.CSSProperties = { display: "block", width: "100%", height: "auto", maxHeight: 1250, objectFit: "cover", scale: kb };
  const imgOver: React.CSSProperties = { position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", scale: kb };
  const tag = (text: string, side: "left" | "right", bg: string) => (
    <div style={{ position: "absolute", top: 28, [side]: 28, padding: "10px 30px", borderRadius: 999, background: bg,
                  color: "#FFFFFF", fontFamily: FONT_STACK, fontWeight: 900, fontSize: 52,
                  boxShadow: "0 6px 16px rgba(0,0,0,0.35)" }}>{text}</div>
  );
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "relative", width: BW, borderRadius: 30, overflow: "hidden", marginTop: -80,
                    border: "6px solid #FFFFFF", boxShadow: "0 30px 80px rgba(0,0,0,0.55)",
                    scale: interpolate(enter, [0, 1], [0.92, 1]), background: "#000" }}>
        {before ? <Img src={staticFile(before.file)} style={img} /> : null}
        {after ? (
          <div style={{ position: "absolute", inset: 0, clipPath: `inset(0 ${(1 - sweep) * 100}% 0 0)` }}>
            <Img src={staticFile(after.file)} style={imgOver} />
          </div>
        ) : null}
        <div style={{ position: "absolute", top: 0, bottom: 0, left: `calc(${sweep * 100}% - 5px)`, width: 10,
                      background: "#FFFFFF", boxShadow: "0 0 22px rgba(0,0,0,0.5)" }} />
        {tag((before?.label || "Trước").toUpperCase(), "left", "rgba(0,0,0,0.6)")}
        {sweep > 0.5 ? tag((after?.label || "Sau").toUpperCase(), "right", PALETTE.keyBox) : null}
      </div>
    </AbsoluteFill>
  );
};

/** Thanh hẹn giờ đèn (skill v2): 2 hàng "10 PHÚT · ÁNH SÁNG XANH" / "5 PHÚT · ÁNH SÁNG ĐỎ",
 *  hàng 2 sáng lên tại `rows[1].at` (giây tính từ đầu thẻ), mỗi hàng có thanh tiến độ. */
export const LightTimerFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  // Feedback lo-08 (2026-10-16): TỪNG thẻ một (10′ xanh → đúng lúc đèn chuyển đỏ thì thay bằng 5′ đỏ cùng chỗ), một hàng
  // ~170 px để đặt thấp trong vùng an toàn (không sát mép trên bị TikTok che); màu cố định "kính tối" — nền đen mờ,
  // số + viền + thanh tiến độ theo màu đèn, chữ trắng (tương phản 18:1, không theo preset).
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const fade = useFade();
  const rows = (item.rows?.length ? item.rows : [
    { min: 10, title: "ÁNH SÁNG XANH", sub: "kích hoạt gel", color: "blue" as const, at: 0 },
    { min: 5, title: "ÁNH SÁNG ĐỎ", sub: "làm dịu nướu", color: "red" as const, at: (durationInFrames / fps) * 0.55 },
  ]).slice(0, 2);
  const GLASS = { blue: { edge: "#40A0FF", num: "#60B4FF", glow: "64, 160, 255" },
                  red: { edge: "#FF4D4D", num: "#FF6363", glow: "255, 77, 77" } };
  const starts = rows.map((r) => Math.round((r.at ?? 0) * fps));
  let k = 0;
  starts.forEach((f, i) => { if (frame >= f) k = i; });
  const r = rows[k];
  const from = starts[k];
  const to = k + 1 < rows.length ? starts[k + 1] : durationInFrames;
  const c = GLASS[r.color];
  const enter = spring({ frame: frame - from, fps, config: { damping: 14, stiffness: 200 } });
  // thẻ cũ trượt ra trong 6 khung trước khi thẻ mới vào
  const out = k + 1 < rows.length ? interpolate(frame, [to - 6, to], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 1;
  const prog = interpolate(frame, [from, Math.max(from + 1, to)], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const pulse = 0.55 + 0.45 * Math.abs(Math.sin((frame / fps) * Math.PI * 1.2));
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div style={{ position: "absolute", top: `${(item.y ?? 0.13) * 100}%`, width: 680, boxSizing: "border-box",
                    display: "flex", flexDirection: "column", gap: 8, padding: "18px 30px", borderRadius: 28,
                    fontFamily: FONT_STACK, background: "rgba(20, 18, 24, 0.92)", border: `5px solid ${c.edge}`,
                    boxShadow: `0 0 ${24 + 16 * pulse}px rgba(${c.glow}, 0.55), 0 14px 30px rgba(0,0,0,0.4)`,
                    opacity: Math.min(1, enter * 1.4) * out,
                    translate: `${interpolate(enter, [0, 1], [-40, 0]) + interpolate(out, [0, 1], [40, 0])}px 0px` }}>
        <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
          <span style={{ fontWeight: 900, fontSize: 72, lineHeight: 1, color: c.num, whiteSpace: "nowrap" }}>{r.min} PHÚT</span>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            <span style={{ fontWeight: 900, fontSize: 36, lineHeight: 1.05, color: "#FFFFFF", whiteSpace: "nowrap" }}>{r.title}</span>
            <span style={{ fontWeight: 700, fontSize: 28, color: "rgba(255,255,255,0.88)", whiteSpace: "nowrap" }}>{r.sub}</span>
          </div>
        </div>
        <div style={{ height: 9, borderRadius: 5, background: "rgba(255,255,255,0.16)" }}>
          <div style={{ width: `${prog * 100}%`, height: "100%", borderRadius: 5, background: c.edge }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** Kinetic hook (skill v2, preset kinetic): 1–1,5 s đầu, từng cụm chữ cỡ 150 px đập lên trong vùng an toàn.
 *  `words`: các cụm; cụm viết *như này* tô màu nhấn. */
export const KineticFx: React.FC<{ item: GraphicItem; safe: Safe }> = ({ item, safe }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const words = item.words?.length ? item.words : (item.label || "").split(/\s+/).filter(Boolean);
  if (!words.length) return null;
  const per = Math.max(1, Math.floor(durationInFrames / words.length));
  const k = Math.min(words.length - 1, Math.floor(frame / per));
  const hit = spring({ frame: frame - k * per, fps, config: { damping: 10, stiffness: 320 } });
  const exit = interpolate(frame, [durationInFrames - 4, durationInFrames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const word = words[k];
  const accent = /^\*.*\*$/.test(word);
  // `y` (0–1) = mép trên khối chữ; đặt né mặt/răng. Khối 2 dòng ~320 px; chạm hàng cột nút thì lệch trái (chừa rail_w)
  const top = Math.max(safe.top, Math.min((item.y ?? 0) > 0 ? (item.y as number) * 1920 : safe.top + 120, 1920 - safe.bottom - 320));
  const right = top + 320 > safe.rail_top ? safe.rail_w : safe.side;
  return (
    <AbsoluteFill style={{ opacity: exit }}>
      <div style={{ position: "absolute", top, left: safe.side, right, display: "flex", justifyContent: "center" }}>
      <div style={{ fontFamily: FONT_STACK, fontWeight: 900, fontSize: 150, lineHeight: 1, textAlign: "center",
                    textTransform: "uppercase", color: accent ? PALETTE.marker : "#FFFFFF", maxWidth: 1080 - safe.side - right,
                    WebkitTextStroke: "12px #111111", paintOrder: "stroke fill",
                    scale: interpolate(hit, [0, 1], [1.25, 1]), rotate: `${k % 2 ? 2 : -2}deg` }}>
        {word.replace(/^\*|\*$/g, "")}
      </div>
      </div>
    </AbsoluteFill>
  );
};

/** Thẻ CTA cuối (skill v2): nút CTA + dòng phụ + huy hiệu LIVE tuỳ chọn, trong vùng an toàn (lệch trái ở hàng cột nút). */
export const EndCardFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useFade();
  const enter = spring({ frame, fps, config: { damping: 12, stiffness: 200, overshootClamping: true } });
  const pulse = 1 + 0.035 * Math.sin((frame / fps) * Math.PI * 3);
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div style={{ position: "absolute", top: `${(item.y ?? 0.5) * 100}%`, width: 620, display: "flex", flexDirection: "column",
                    alignItems: "center", gap: 14, fontFamily: FONT_STACK, scale: interpolate(enter, [0, 1], [0.7, 1]) }}>
        {item.live ? (
          <div style={{ padding: "6px 22px", borderRadius: 10, background: "#FF2D55", color: "#FFFFFF", fontWeight: 900,
                        fontSize: 34, letterSpacing: "0.12em" }}>● LIVE</div>
        ) : null}
        <div style={{ borderRadius: 999, background: PALETTE.keyBox, color: "#FFFFFF", fontWeight: 900,
                      fontSize: 64, textTransform: "uppercase", boxShadow: "0 18px 40px rgba(0,0,0,0.35)", scale: pulse,
                      maxWidth: 620, boxSizing: "border-box", textAlign: "center", lineHeight: 1.1, whiteSpace: "nowrap",
                      padding: "20px 40px" }}>
          {plainText(item.label || "Bấm giỏ hàng")}
        </div>
        {item.sub ? (
          <div style={{ padding: "8px 22px", borderRadius: 14, background: "rgba(20, 12, 20, 0.8)", color: "#FFFFFF",
                        fontWeight: 700, fontSize: 44 }}>{plainText(item.sub)}</div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

/** Chuyển cảnh preset vox ở ranh giới chương: tờ giấy có hạt lướt ngang qua khung trong ~0,3 s (không nháy trắng). */
export const PaperSwipeFx: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const x = interpolate(frame, [0, durationInFrames], [1180, -1180], { easing: Easing.inOut(Easing.cubic) });
  return (
    <AbsoluteFill style={{ translate: `${x}px 0px`, rotate: "-3deg", scale: 1.15 }}>
      <AbsoluteFill style={{ background: PALETTE.paper, boxShadow: "0 0 60px rgba(0,0,0,0.35)" }} />
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, opacity: 0.35, mixBlendMode: "multiply" }}>
        <filter id="grain2">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={7} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#grain2)" />
      </svg>
    </AbsoluteFill>
  );
};


/** Các bước cách dùng (educate): bước đang nói sáng lên.
 *  `steps`: "TIÊU ĐỀ | dòng phụ" (dòng phụ tuỳ chọn). `times` (giây từ đầu thẻ) = lúc người nói nói tới bước i —
 *  bước chỉ hiện khi được nói (lo-05: không đợi nói xong mới tóm tắt); thiếu `times` thì chia đều.
 *  `compact`: thẻ gọn ~230 px — hàng chấm tiến độ + đúng một bước đang nói (đặt nửa dưới khi nguồn có phụ đề ở trên). */
export const StepsFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const fade = useFade();
  const steps = (item.steps ?? []).slice(0, 5).map((s) => {
    const [title, sub] = s.split("|").map((x) => x.trim());
    return { title, sub };
  });
  const per = Math.max(1, (durationInFrames - FADE * 2) / Math.max(1, steps.length));
  const timed = (item.times?.length ?? 0) > 0;
  const startAt = steps.map((_, i) =>
    timed && (item.times as number[]).length > i ? Math.round((item.times as number[])[i] * fps) : FADE + Math.round(i * per));
  let current = 0;
  startAt.forEach((f, i) => { if (frame >= f) current = i; });
  if (item.compact) {
    const st = steps[current] ?? { title: "", sub: "" };
    const p = spring({ frame: frame - startAt[current], fps, config: { damping: 14, stiffness: 210 } });
    return (
      <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
        <div style={{ position: "absolute", top: `${(item.y ?? 0.55) * 100}%`, width: 600, display: "flex",
                      flexDirection: "column", gap: 10, fontFamily: FONT_STACK }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            {item.label ? (
              <div style={{ padding: "4px 16px", borderRadius: 999, background: PALETTE.keyBox, color: "#FFFFFF",
                            fontWeight: 900, fontSize: 28, letterSpacing: "0.04em", whiteSpace: "nowrap" }}>{plainText(item.label)}</div>
            ) : null}
            {steps.map((_, i) => {
              const done = i < current, on = i === current, seen = frame >= startAt[i];
              return (
                <div key={i} style={{ width: 44, height: 44, borderRadius: "50%", display: "flex", alignItems: "center",
                                      justifyContent: "center", fontWeight: 900, fontSize: 26,
                                      background: on ? PALETTE.pink : done ? "rgba(255,255,255,0.85)" : "rgba(20,12,20,0.55)",
                                      color: on || done ? PALETTE.plum : "rgba(255,255,255,0.7)",
                                      border: `3px solid ${seen ? PALETTE.pink : "rgba(255,255,255,0.25)"}`,
                                      scale: on ? interpolate(p, [0, 1], [1.35, 1.1]) : 1 }}>
                  {done ? "✓" : i + 1}
                </div>
              );
            })}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 16, padding: "12px 22px", borderRadius: 22,
                        background: PALETTE.plumCard, border: `3px solid ${PALETTE.pink}`, alignSelf: "flex-start",
                        boxShadow: "0 14px 30px rgba(0,0,0,0.3)", opacity: Math.min(1, p * 1.5),
                        translate: `${interpolate(p, [0, 1], [-50, 0])}px 0px` }}>
            <div style={{ width: 58, height: 58, flex: "0 0 58px", borderRadius: "50%", display: "flex", alignItems: "center",
                          justifyContent: "center", fontWeight: 900, fontSize: 34, background: PALETTE.pink, color: PALETTE.plum }}>
              {current + 1}
            </div>
            <div>
              <div style={{ fontWeight: 900, fontSize: 42, lineHeight: 1.05, color: PALETTE.cardText, textTransform: "uppercase",
                            whiteSpace: "nowrap" }}>{plainText(st.title)}</div>
              {st.sub ? <div style={{ fontWeight: 700, fontSize: 28, color: PALETTE.cardText, opacity: 0.85 }}>{plainText(st.sub)}</div> : null}
            </div>
          </div>
        </div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div style={{ position: "absolute", top: `${(item.y ?? 0.15) * 100}%`, width: 620, display: "flex",
                    flexDirection: "column", gap: 12, fontFamily: FONT_STACK }}>
        {item.label ? (
          <div style={{ alignSelf: "flex-start", padding: "6px 20px", borderRadius: 999, background: PALETTE.keyBox,
                        color: "#FFFFFF", fontWeight: 900, fontSize: 34, letterSpacing: "0.04em" }}>{plainText(item.label)}</div>
        ) : null}
        {steps.map((st, i) => {
          const at = timed ? startAt[i] : FADE + Math.round(i * per * 0.35);
          const p = spring({ frame: frame - at, fps, config: { damping: 15, stiffness: 190 } });
          const on = i === current;
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 18, padding: "12px 20px", borderRadius: 22,
                                  background: on ? PALETTE.plumCard : "rgba(20, 12, 20, 0.62)",
                                  border: `3px solid ${on ? PALETTE.pink : "rgba(255,255,255,0.12)"}`,
                                  opacity: Math.min(1, p * 1.4), translate: `${interpolate(p, [0, 1], [-60, 0])}px 0px` }}>
              <div style={{ width: 64, height: 64, flex: "0 0 64px", borderRadius: "50%", display: "flex",
                            alignItems: "center", justifyContent: "center", fontWeight: 900, fontSize: 38,
                            background: on ? PALETTE.pink : "rgba(255,255,255,0.18)", color: on ? PALETTE.plum : "#FFFFFF" }}>
                {i + 1}
              </div>
              <div>
                <div style={{ fontWeight: 900, fontSize: 44, lineHeight: 1.05, color: "#FFFFFF", textTransform: "uppercase" }}>
                  {plainText(st.title)}
                </div>
                {st.sub ? <div style={{ fontWeight: 700, fontSize: 30, color: "rgba(255,255,255,0.8)" }}>{plainText(st.sub)}</div> : null}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/** Chữ có *nhấn* (hồng) / [nhấn 2] (xanh) cho các thẻ đồ hoạ mới. */
const Rich: React.FC<{ text: string; accent?: string }> = ({ text, accent }) => (
  <>
    {parseRich(text).map((p, i) => (
      <span key={i} style={{ color: p.tone === "accent" ? accent ?? PALETTE.pink : p.tone === "accent2" ? PALETTE.accent2 : undefined }}>
        {p.t}
      </span>
    ))}
  </>
);

/** Nỗi đau cách cũ (lo-05): icon miếng dán trắng răng bật vào → hai nét gạch chéo đỏ vẽ ra → nhãn rung nhẹ. */
export const NopeFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useFade();
  const pop = spring({ frame, fps, config: { damping: 11, stiffness: 220 } });
  const s1 = interpolate(frame, [8, 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const s2 = interpolate(frame, [13, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const lab = spring({ frame: frame - 18, fps, config: { damping: 9, stiffness: 260 } });
  const shake = frame > 18 && frame < 34 ? 6 * Math.sin(frame * 1.9) * (1 - (frame - 18) / 16) : 0;
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div style={{ position: "absolute", top: `${(item.y ?? 0.4) * 100}%`, width: 560, display: "flex",
                    flexDirection: "column", alignItems: "center", gap: 6, fontFamily: FONT_STACK }}>
        <svg width={300} height={166} viewBox="0 0 360 200" style={{ scale: interpolate(pop, [0, 1], [0.5, 1]),
             filter: "drop-shadow(0 10px 18px rgba(0,0,0,0.35))" }}>
          {/* miếng dán: dải cong trong suốt có lớp gel */}
          <path d="M40 80 Q180 20 320 80 L320 128 Q180 70 40 128 Z" fill="rgba(255,255,255,0.92)" stroke="#9AA7B8" strokeWidth={5} />
          <path d="M70 92 Q180 48 290 92" fill="none" stroke="#CFE6FF" strokeWidth={10} strokeLinecap="round" />
          <line x1={70} y1={30} x2={70 + 220 * s1} y2={30 + 150 * s1} stroke="#E62828" strokeWidth={22} strokeLinecap="round" />
          <line x1={290} y1={30} x2={290 - 220 * s2} y2={30 + 150 * s2} stroke="#E62828" strokeWidth={22} strokeLinecap="round" />
        </svg>
        <div style={{ padding: "10px 30px", borderRadius: 20, background: PALETTE.plumCard, color: PALETTE.cardText, fontWeight: 900,
                      fontSize: 58, textTransform: "uppercase", whiteSpace: "nowrap", opacity: Math.min(1, lab * 1.5),
                      scale: interpolate(lab, [0, 1], [1.3, 1]), translate: `${shake}px 0px`,
                      boxShadow: "0 14px 30px rgba(0,0,0,0.3)" }}>
          <Rich text={item.label || "*Ê BUỐT*"} accent="#FF6B6B" />
        </div>
        {item.sub ? (
          <div style={{ padding: "6px 20px", borderRadius: 14, background: "rgba(20, 12, 20, 0.78)", color: "#FFFFFF",
                        fontWeight: 700, fontSize: 34, opacity: Math.min(1, lab * 1.5) }}>{plainText(item.sub)}</div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

/** Cột so sánh chi phí (lo-05): cột trái (cách khác, vd nha khoa) mọc lên trước, cột phải chỉ cao `ratio` × cột trái,
 *  nhãn `label` ("CHỈ *1/3*") bật vào. Không ghi giá tiền — chỉ tỉ lệ người nói nói ra. */
export const CostCompareFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useFade();
  const H = 230;
  const g1 = spring({ frame: frame - 2, fps, config: { damping: 16, stiffness: 120 } });
  const g2 = spring({ frame: frame - 14, fps, config: { damping: 13, stiffness: 160 } });
  const lab = spring({ frame: frame - 24, fps, config: { damping: 10, stiffness: 240 } });
  const ratio = Math.min(1, Math.max(0.1, item.ratio ?? 1 / 3));
  const col = (h: number, color: string, name: string, k: number, hl: boolean) => (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8, width: 170 }}>
      <div style={{ height: H, display: "flex", alignItems: "flex-end" }}>
        <div style={{ width: 130, height: h * k, borderRadius: "18px 18px 6px 6px", background: color,
                      boxShadow: hl ? `0 0 0 5px #FFFFFF, 0 12px 28px rgba(0,0,0,0.35)` : "0 12px 28px rgba(0,0,0,0.3)" }} />
      </div>
      <div style={{ padding: "6px 14px", borderRadius: 12, background: hl ? PALETTE.keyBox : "rgba(20,12,20,0.8)",
                    color: "#FFFFFF", fontWeight: 900, fontSize: 32, whiteSpace: "nowrap" }}>{plainText(name)}</div>
    </div>
  );
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div style={{ position: "absolute", top: `${(item.y ?? 0.4) * 100}%`, width: 480, display: "flex",
                    flexDirection: "column", alignItems: "center", gap: 10, fontFamily: FONT_STACK }}>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 30, position: "relative" }}>
          {col(H, "rgba(160, 160, 175, 0.92)", item.left_label || "CÁCH KHÁC", g1, false)}
          {col(H * ratio, PALETTE.pink, item.right_label || BRAND.label || "CỦA MÌNH", g2, true)}
          <div style={{ position: "absolute", right: -20, top: H * (1 - ratio) - 100, padding: "8px 20px", borderRadius: 18,
                        background: PALETTE.plumCard, color: PALETTE.cardText, fontWeight: 900, fontSize: 56, whiteSpace: "nowrap",
                        opacity: Math.min(1, lab * 1.5), scale: interpolate(lab, [0, 1], [1.4, 1]), rotate: "-4deg",
                        boxShadow: "0 14px 30px rgba(0,0,0,0.35)" }}>
            <Rich text={item.label || "CHỈ *1/3*"} />
          </div>
        </div>
        {item.sub ? (
          <div style={{ padding: "6px 20px", borderRadius: 14, background: "rgba(20, 12, 20, 0.8)", color: "#FFFFFF",
                        fontWeight: 700, fontSize: 34, opacity: Math.min(1, lab * 1.5) }}>{plainText(item.sub)}</div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

/** Phần bổ sung mua lẻ (lo-05, tên cũ gel_refill): bút/lõi bổ sung trượt vào từ trái + huy hiệu "+1" bật lên,
 *  nhãn `label`, dòng phụ `sub`. Chữ trên thân bút = tên thương hiệu của hồ sơ (tokens.brand_label). */
export const RefillFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useFade();
  const slide = spring({ frame, fps, config: { damping: 14, stiffness: 170 } });
  const plus = spring({ frame: frame - 12, fps, config: { damping: 8, stiffness: 260 } });
  const lab = spring({ frame: frame - 8, fps, config: { damping: 13, stiffness: 200 } });
  const bob = 4 * Math.sin((frame / fps) * Math.PI * 1.4);
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div style={{ position: "absolute", top: `${(item.y ?? 0.45) * 100}%`, width: 600, display: "flex",
                    alignItems: "center", gap: 18, fontFamily: FONT_STACK }}>
        <div style={{ position: "relative", width: 170, height: 260, flex: "0 0 170px",
                      translate: `${interpolate(slide, [0, 1], [-160, 0])}px ${bob}px`, rotate: "-18deg", opacity: Math.min(1, slide * 1.5) }}>
          <svg width={170} height={260} viewBox="0 0 170 260" style={{ filter: "drop-shadow(0 10px 16px rgba(0,0,0,0.35))" }}>
            {/* bút bổ sung: thân trong, ruột xanh, nắp màu nhấn, chữ thương hiệu */}
            <rect x={60} y={60} width={50} height={170} rx={16} fill="rgba(255,255,255,0.95)" stroke="#B9C3CF" strokeWidth={4} />
            <rect x={66} y={110} width={38} height={100} rx={10} fill="#DDEFFF" />
            <rect x={56} y={18} width={58} height={52} rx={14} fill={PALETTE.pink} />
            <rect x={78} y={4} width={14} height={18} rx={5} fill="#FFFFFF" stroke="#B9C3CF" strokeWidth={3} />
            <text x={85} y={175} textAnchor="middle" fontFamily={FONT_STACK} fontWeight={900} fontSize={20} fill="#E0245E"
                  transform="rotate(-90 85 175)">{BRAND.label.toLowerCase()}</text>
          </svg>
          <div style={{ position: "absolute", right: -16, top: 0, width: 74, height: 74, borderRadius: "50%",
                        background: PALETTE.keyBox, color: "#FFFFFF", fontWeight: 900, fontSize: 38, display: "flex",
                        alignItems: "center", justifyContent: "center", rotate: "18deg", border: "4px solid #FFFFFF",
                        scale: interpolate(plus, [0, 1], [0, 1]) }}>+1</div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8, opacity: Math.min(1, lab * 1.5),
                      translate: `${interpolate(lab, [0, 1], [40, 0])}px 0px` }}>
          <div style={{ padding: "10px 22px", borderRadius: 18, background: PALETTE.plumCard, color: PALETTE.cardText,
                        fontWeight: 900, fontSize: 52, lineHeight: 1.08, textTransform: "uppercase",
                        boxShadow: "0 14px 30px rgba(0,0,0,0.3)" }}>
            <Rich text={item.label || "HẾT? *MUA LẺ*"} />
          </div>
          {item.sub ? (
            <div style={{ alignSelf: "flex-start", padding: "6px 18px", borderRadius: 14, background: "rgba(20, 12, 20, 0.8)",
                          color: "#FFFFFF", fontWeight: 700, fontSize: 32 }}>{plainText(item.sub)}</div>
          ) : null}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/** CTA bấm vào live: huy hiệu ● ĐANG LIVE nhấp nháy + nút + mũi tên nhịp chỉ sang phải (về phía avatar ở cột nút).
 *  Mọi thứ nằm trong vùng an toàn; mũi tên dừng ở mép khoảng an toàn. */
export const LiveCtaFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useFade();
  const enter = spring({ frame, fps, config: { damping: 12, stiffness: 200, overshootClamping: true } });
  const blink = 0.55 + 0.45 * Math.abs(Math.sin((frame / fps) * Math.PI * 1.6));
  const nudge = 14 * Math.max(0, Math.sin((frame / fps) * Math.PI * 2.2));
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div style={{ position: "absolute", top: `${(item.y ?? 0.5) * 100}%`, width: 620, display: "flex",
                    flexDirection: "column", alignItems: "center", gap: 14, fontFamily: FONT_STACK,
                    scale: interpolate(enter, [0, 1], [0.7, 1]) }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "8px 24px", borderRadius: 12,
                      background: "#FF2D55", color: "#FFFFFF", fontWeight: 900, fontSize: 36, letterSpacing: "0.1em" }}>
          <span style={{ width: 18, height: 18, borderRadius: "50%", background: "#FFFFFF", opacity: blink }} />
          ĐANG LIVE
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div style={{ padding: "18px 38px", borderRadius: 999, background: PALETTE.keyBox, color: "#FFFFFF",
                        fontWeight: 900, fontSize: 60, textTransform: "uppercase", whiteSpace: "nowrap",
                        boxShadow: "0 18px 40px rgba(0,0,0,0.35)" }}>
            {plainText(item.label || "Bấm vào live")}
          </div>
          <svg width={90} height={60} viewBox="0 0 90 60" style={{ translate: `${nudge}px 0px` }}>
            <path d="M6 30 H70 M50 10 L74 30 L50 50" fill="none" stroke="#FFFFFF" strokeWidth={10}
                  strokeLinecap="round" strokeLinejoin="round" style={{ filter: "drop-shadow(0 3px 4px rgba(0,0,0,0.5))" }} />
          </svg>
        </div>
        {item.sub ? (
          <div style={{ padding: "8px 22px", borderRadius: 14, background: "rgba(20, 12, 20, 0.8)", color: "#FFFFFF",
                        fontWeight: 700, fontSize: 40 }}>{plainText(item.sub)}</div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

/** CÁCH CŨ vs <thương hiệu> (lo-06): hai cột nổi trên video — cột trái xám ✗ (cách cũ), cột phải màu nhấn ✓.
 *  `steps`: "ý trái | ý phải", hiện lần lượt từng dòng; cột phải sáng lên + nảy nhẹ sau cột trái. */
export const VersusFx: React.FC<{ item: GraphicItem }> = ({ item }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const fade = useFade();
  const rows = (item.steps ?? []).slice(0, 3).map((s) => {
    const [l, r] = s.split("|").map((x) => x.trim());
    return { l, r: r ?? "" };
  });
  const head = spring({ frame, fps, config: { damping: 14, stiffness: 190 } });
  const right = spring({ frame: frame - 12, fps, config: { damping: 11, stiffness: 220 } });
  const col = (title: string, mark: string, on: boolean, k: number) => (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 8, padding: "14px 16px", borderRadius: 22,
                  background: on ? PALETTE.plumCard : "rgba(40, 36, 44, 0.78)",
                  border: `3px solid ${on ? PALETTE.pink : "rgba(255,255,255,0.15)"}`,
                  boxShadow: on ? "0 14px 30px rgba(0,0,0,0.35)" : "0 10px 22px rgba(0,0,0,0.25)",
                  opacity: Math.min(1, k * 1.5), scale: on ? interpolate(k, [0, 1], [0.85, 1.04]) : interpolate(k, [0, 1], [0.9, 1]) }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{ width: 46, height: 46, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
                      fontWeight: 900, fontSize: 30, color: "#FFFFFF", background: on ? "#22C55E" : "#E62828" }}>{mark}</div>
        <div style={{ fontWeight: 900, fontSize: 38, lineHeight: 1.05, color: on ? PALETTE.pink : "rgba(255,255,255,0.75)",
                      textTransform: "uppercase", whiteSpace: "nowrap" }}>{plainText(title)}</div>
      </div>
      {rows.map((row, i) => {
        const p = spring({ frame: frame - (on ? 16 : 6) - i * 7, fps, config: { damping: 15, stiffness: 200 } });
        return (
          <div key={i} style={{ fontWeight: on ? 900 : 700, fontSize: 32, lineHeight: 1.1, whiteSpace: "nowrap",
                                color: on ? PALETTE.cardText : "rgba(255,255,255,0.6)", opacity: Math.min(1, p * 1.5),
                                textDecoration: on ? "none" : "line-through", textDecorationColor: "rgba(230,40,40,0.8)",
                                translate: `${interpolate(p, [0, 1], [on ? 24 : -24, 0])}px 0px` }}>
            {plainText(on ? row.r : row.l)}
          </div>
        );
      })}
    </div>
  );
  return (
    <AbsoluteFill style={{ opacity: fade, alignItems: "center" }}>
      <div style={{ position: "absolute", top: `${(item.y ?? 0.4) * 100}%`, width: 600, display: "flex", gap: 14,
                    alignItems: "stretch", fontFamily: FONT_STACK }}>
        {col(item.left_label || "CÁCH CŨ", "✗", false, head)}
        {col(item.right_label || BRAND.label || "CÁCH MỚI", "✓", true, right)}
      </div>
    </AbsoluteFill>
  );
};
