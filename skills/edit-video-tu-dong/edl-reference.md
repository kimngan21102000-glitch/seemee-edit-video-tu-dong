# Viết `jobs/<lô>/edl.json` — tham chiếu

Schema: `vf/edl.py` (docstring `Graphic` liệt kê mọi đồ hoạ), mẫu `templates/edl.example.json` (lô Smilee lo-08 cũ: `git show 6a95acb:examples/smilee-lo-08/edl.json`). Mọi thời gian `overlays`/`graphics`/`effects` theo **timeline output** (giây, 0 = đầu video).
Đọc đủ trước khi viết: brief, style guide chung + của hồ sơ, tokens của hồ sơ, `product.md`, hooks/learnings,
`work/<nguồn>/transcript.json`, `keep.json`, `info.json`, `scenes.json` của MỌI nguồn, MỌI trang `*_sheet_NNN.png`.

## Biến thể
- Đúng `brief.variants` biến thể (mặc định 4 cấu trúc — style guide chung mục 2), **khác nhau rõ về kiểu hook hoặc preset** — không chỉ khác chữ. Render ghi `hook trùng với …` khi hai bản dùng chung đoạn hook.
- `hook_type`: `pain` | `question` | `result_first` | `contrarian` | `cost_compare` | `cta_first`. Không mở đầu bằng giá.
- `preset` (đúng 1): tên trong `profiles/<hồ sơ>/tokens.json → presets` (`vf profiles` liệt kê). Chọn theo style guide của hồ sơ + `learnings-stats.md`.
- `rationale`: 1–2 câu vì sao biến thể có thể thắng (+ lý do nếu để lại ghi chú `~`).
- Bản cắt ngắn (brief có `cutdown_seconds`): `"cutdown_of": "<id>"`, id `<id>-ngan`, giữ hook + bằng chứng mạnh nhất + CTA.

## Đoạn (hook + segments)
- Hook ≤ 3 s, **khung đầu là hình mạnh nhất** (cảnh tiền của ngành); câu có lực nhất cho kiểu hook đó, lấy từ đâu trong nguồn cũng được.
- **Thứ tự**: nỗi đau/lợi ích → hiệu quả → hiệu quả nhanh → trước/sau (hiệu quả/bằng chứng trong 45 % đầu); cách dùng, giá trị/tiết kiệm ở giữa; **khen kết ngay trước CTA**. Tiện ích phụ `chapter: "extra"` chỉ giữ khi đang trong chuỗi liệt kê khen; nói xong ý chính thì bỏ. Lint báo `thứ tự: …`.
- Mỗi đoạn `chapter`: `pain`, `benefit`, `result`, `proof`, `speed`, `saving`, `cta`, `extra` (hook tự là `hook`; không ghi = chương của đoạn trước). **Đủ ý** theo `tokens.content_checklist` — lint báo chương thiếu.
- Tổng thời lượng: `target_seconds ± 10 %`.
- **Mép tiếng** (style guide chung mục 3.1): đầu = đầu chữ phiên âm − 0,02 s; cuối = trũng âm lượng đầu tiên SAU cuối chữ (≤ 0,3 s). Nguồn sạch: `vf snap <lô>` sau khi viết/sinh edl (script sinh edl ghi đè thì chạy lại). Nguồn có nhạc nền: **không** snap. `video_end` khi câu nói tràn qua điểm chuyển cảnh. Lint `cắt giữa từ` / `dính tiếng` là lỗi thật.
- **Mép đoạn ở đầu câu/ý**: không bỏ chữ đầu câu, không cắt giữa từ; render báo `mất chữ đầu câu`, `cắt giữa từ`, `đứng hình`.
- Chỉ lấy đoạn trong `keep.json`. Mép đoạn cách điểm chuyển cảnh (`scenes.json`) ≥ 0,5 s hoặc trùng đúng điểm đó; `vf snap` kéo mép lùi qua điểm chuyển cảnh thì ghim lại.
- Mỗi cảnh ≥ 1,2 s (nhắm 2–4 s); chuỗi dựng nhanh của nguồn thay bằng một cảnh dài + `counter`, hoặc `rapid: true` nếu cố ý.
- Cảnh tiền: `protect: true`, ≥ 2,5 s, để cảnh gốc chạy trọn rồi mới thêm đồ hoạ.
- Không lấy đoạn có clip người sáng tạo/người nổi tiếng khác chèn trong nguồn.
- `source` là tên file nguồn (kèm đuôi). `a_roll` mang lời nói, `b_roll` chèn minh hoạ. Tôn trọng `must_keep`, `must_cut`.

## Chữ (`overlays`)
- `style` theo `overlay_style` của preset: `lower` (thẻ 2 tầng: `text` 2–6 từ viết hoa + `sub` ≤ 8 từ), `vox`, `plain`; dùng chung: `tag` (TRƯỚC/SAU ✓), `cta`, `hook`, `commit`. Lint báo trộn hệ chữ (thẻ CTA được miễn).
- Nhấn màu: `*từ*` = accent, `[từ]` = accent2, tối đa 2 cụm. Số luôn nhấn (danh sách số riêng ở style guide của hồ sơ).
- `animation`: `pop`, `word_by_word` (hook), `highlight` + `emphasis`, `slide`, `none`.
- Chữ đầu tiên ≤ 0,3 s. ≤ 3,5 từ/giây; tối đa 2 khối chữ cùng lúc; chữ tự kéo dài nhưng không vắt qua điểm cắt, không lấn khỏi `text_free` — viết đủ ngắn.
- Không cắt cảnh trong 0,4 s sau khi chữ hiện. Không đặt chữ `center` trên đoạn `protect`.
- **Nguồn trong `text_sources`**: chữ chỉ trong `text_free`; render tự bỏ chữ ngoài các khoảng đó.
- **Vùng an toàn / né mặt**: đừng ghi `y` — render tự đặt `y`, `xc`, bề rộng, né mặt. Phụ đề in sẵn: `avoid: [[y0, y1]]`. Thẻ cần cỡ gốc mà chỗ trống nhỏ: `free: true` (chỉ né mặt).
- **Cam kết** trong `profiles/<hồ sơ>/commitments.txt` tự highlight khi người nói nói ra; ưu tiên giữ các đoạn đó, được đưa lên hook. Không disclaimer; chỉ chặn cụm brief ghi trong `forbidden`.
- Tránh dấu gạch trong cụm số dài ("600–700K") — viết gọn ("TỪ 600K").
- Không phụ đề toàn bộ lời (`captions: false`) trừ khi brief yêu cầu.
- CTA: một CTA mềm trong 60–85 % thời lượng + `end_card` (hoặc thẻ `cta`) trong 3 s cuối — **một lệnh**.

## Đồ hoạ (`graphics`) và hiệu ứng (`effects`)
Chỉ thêm ở đoạn nguồn "trơn"; đoạn nguồn đã tự minh hoạ cùng ý thì để nguyên. Chỉ minh hoạ đúng điều KOL đang nói — không chip teaser rời. Chỉ dùng đồ hoạ thuộc gói hồ sơ đã bật (`graphics_packs`; render báo lỗi nếu sai). Trường để trống được điền theo `tokens.graphic_defaults` của hồ sơ (vd tên cột so sánh).

### Gói chung (mọi hồ sơ)
| Ý | Cú pháp |
|---|---|
| Các bước / sáng đúng lúc nói | `{"kind": "steps", "start", "end", "label": "CÁCH DÙNG", "steps": ["TIÊU ĐỀ \| dòng phụ", …], "times": [0, 1.8, 3.5]}`; `compact: true` = thẻ gọn một bước |
| Cách cũ vs sản phẩm | `{"kind": "versus", "steps": ["ý trái \| ý phải", …], "left_label", "right_label"}` |
| So chi phí | `{"kind": "cost_compare", "ratio": 0.33, "label": "CHỈ *1/3*", "left_label", "right_label"}` — chỉ tỉ lệ người nói nói ra |
| Gạch chéo cách cũ | `{"kind": "nope", "label": "*Ê BUỐT*"}` |
| Phần bổ sung mua lẻ | `{"kind": "refill", "label": "HẾT GEL? *MUA LẺ*", "sub": "…"}` (tên cũ `gel_refill`) |
| Đếm ngày | `{"kind": "counter", "label": "dùng đều mỗi ngày", "days": 7}` 1–1,5 s giữa cảnh trước và sau |
| Khoanh chi tiết | `effects` `zoom_to` + `graphics` `{"kind": "callout", "label": "…", "cx", "cy", "rx", "ry"}` |
| Trước/sau | sau cảnh gốc: `{"kind": "wipe", "stills": [{"source", "t", "crop": [x0,y0,x1,y1], "label": "Trước"}, {…, "label": "Sau 7 ngày"}]}` hoặc `collage` (giấy, preset vox) |
| Kinetic hook | `{"kind": "kinetic", "start": 0, "end": 1.4, "words": ["…", "*…*"]}` |
| Bấm vào live | `{"kind": "live_cta", "label": "Bấm vào live", "sub": "…"}` |
| CTA cuối | `{"kind": "end_card", "label": "BẤM GIỎ HÀNG", "sub": "…", "live": true}` 2,5–3 s cuối |
| Nhấn nhịp | `effects` `zoom_punch` ở chỗ nhấn (không zoom mỗi câu); không `flash`, hạn chế `shake` |

### Gói `nha_khoa` (Smilee)
| Ý | Cú pháp |
|---|---|
| Đèn xanh/đỏ | `{"kind": "light_timer", "rows": [{"min": 10, "title": "ÁNH SÁNG XANH", "sub": "kích hoạt gel", "color": "blue", "at": 0}, {"min": 5, "title": "ÁNH SÁNG ĐỎ", "sub": "làm dịu nướu", "color": "red", "at": 3.2}]}` — từng thẻ một, màu "kính tối" |
| Răng vàng → trắng | `{"kind": "teeth", "split": 0.56}` (hàm răng vector) hoặc `whiten` (icon, ghi "Hình minh họa") |
| Bám răng | `effects` `{"kind": "zoom_to", "zoom": 1.6, "track": "teeth"}` + `callout` `cy: 0.34` |
| Thang màu | `{"kind": "shade", "from_shade": 10, "to_shade": 5, "label": "theo trải nghiệm của …", "days": 0}` — chỉ số mức người nói nói ra |

### Gói `balo` (khung — tinh chỉnh khi có source đầu tiên)
| Ý | Cú pháp |
|---|---|
| Vừa laptop / kích thước | `{"kind": "size_fit", "label": "VỪA LAPTOP *15,6″*", "sub": "45 × 30 × 15 cm"}` |
| Checklist ngăn | `{"kind": "compartments", "label": "BÊN TRONG CÓ GÌ", "steps": ["NGĂN LAPTOP \| chống sốc", …], "times": [0, 1.4, 2.8]}` |
| Huy hiệu | `{"kind": "badge", "icon": "water", "label": "*CHỐNG NƯỚC*", "sub": "vải Oxford 900D"}` — icon: water, material, weight, zip, warranty, star |

Chuyển cảnh: mọi preset **cắt thẳng** — không khai tay.

## Âm thanh
Render tự gắn SFX theo sự kiện (`tokens.auto_sfx`, file `library/brand/sfx/`). Khai tay `{"kind": "sfx", "at", "asset": "sfx/ding.wav"}` khi cần; `"sfx_auto": false` để tắt. `music`: nhạc có giấy phép trong `library/brand/` hoặc `profiles/<hồ sơ>/brand/`; nhạc trend thì để trống và ghi "gắn nhạc CML trên TikTok" trong `rationale`. Giữ tiếng ASMR thật.

## Ma trận GMV Max (tuỳ chọn)
`"matrix": {"presets": [...], "hooks": [{"id", "hook_type", "hook": {...}, "overlays": [...]}], "bodies": [{"id", "segments": [...], "overlays", "graphics", "effects"}], "ctas": [...]}` — thời gian trong mỗi phần tính từ đầu phần đó. `vf expand <lô>` thêm biến thể `<lô>_<hook>_<body>_<cta>_<preset>`.
