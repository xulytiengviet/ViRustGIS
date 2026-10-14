# viRustGIS MCP — ChatGPT và AI Agents (2027)

> Trạng thái: MCP stdio **đã có** trong viRustGIS. ChatGPT trên web **không** thể kết nối trực tiếp với tiến trình stdio hoặc điều khiển cửa sổ Desktop hiện mở. HTTPS gateway và desktop IPC là các hạng mục chưa triển khai.

## Sơ đồ triển khai

```text
Claude Desktop / Cursor / VS Code / MCP client (local)
             | MCP over stdio
             v
      rustgis-cli mcp
             | crates/assistant/src/mcp.rs
             v
      rustgis_engine::Session (RIÊNG)
             | Session::run / geoprocessing
             v
      .rgis / layers / rendered PNG

ChatGPT web -> HTTPS Remote MCP gateway (CHƯA TRIỂN KHAI)
                                      |
                                      v
                          policy/auth -> rustgis-cli

Desktop GUI active session <-> IPC bridge (CHƯA TRIỂN KHAI)
```

## Cách chạy thực tế

Biên dịch từ nguồn trên môi trường Rust tương thích:

```powershell
cargo build --release -p rustgis-cli
.\target\release\rustgis-cli.exe mcp --sample
```

Để nạp một project có sẵn, thay `--sample` bằng `--project C:\\GIS\\demo.rgis`. Mặc định quyền truy cập tập tin/mạng bị chặn ở mức MCP; **không thêm `--yes`** trừ khi dữ liệu tin cậy và bạn chấp nhận quyền đọc/ghi. Cần kiểm tra các tùy chọn trên đúng binary trước khi áp dụng trong môi trường sản xuất.

Ví dụ cấu hình MCP client hỗ trợ stdio (điều chỉnh đường dẫn tuyệt đối):

```json
{
  "mcpServers": {
    "viRustGIS": {
      "command": "C:\\\\path\\\\to\\\\viRustGIS\\\\target\\\\release\\\\rustgis-cli.exe",
      "args": ["mcp", "--sample"]
    }
  }
}
```

Hãy đặt đường dẫn với escape JSON đúng theo máy. Chạy `python scripts/mcp_smoke.py --exe target/release/rustgis-cli` để kiểm tra tự động. Script không cần API key và không sửa dữ liệu.

## Công cụ MCP thực có trong mã

- `list_layers`, `view_map`: xem phiên bản đồ đang được MCP sở hữu.
- `search_commands`, `run_command`: tìm và chạy command.
- `search_tools`, `describe_tool`, `run_tool`: tìm và thực thi geoprocessing.
- `read_features`: xem thuộc tính.
- `search_docs`, `read_doc`: tài liệu.

Danh mục chuẩn được lấy từ `tools/list` khi chạy, tránh duy trì danh sách tĩnh dễ sai khác. MCP hỗ trợ `initialize`, `tools/list`, `tools/call`, `resources/list`, `resources/read` và `ping`.

## Các bước để kết nối ChatGPT trên trình duyệt

1. Triển khai **remote MCP gateway** hỗ trợ Streamable HTTP, public HTTPS, xác thực người dùng/OAuth và chính sách cấp quyền cho từng action. Giữ MCP stdio ở máy local; gateway chỉ chuyển tiếp sau khi xác thực và kiểm tra quyền. **Không công khai trực tiếp stdio/localhost** hoặc mở tunnel không kiểm soát.
2. Có cơ chế xác nhận riêng trước thao tác ghi, xóa, ghi đè, chạy script, truy cập mạng hay tệp; `--yes` là cờ quyền rộng, **không** phải cơ chế xác nhận từng thao tác.
3. Dùng giới hạn root directory cho file I/O, allowlist tool/command và giới hạn payload, timeout, concurrency, audit log. Vô hiệu hóa việc thực thi code tùy ý từ nội dung prompt/GeoJSON/metadata.
4. Khi gateway chạy và được kiểm thử, thêm custom MCP connector tương ứng vào ChatGPT nếu tính năng này có trong tài khoản/workspace.
5. Tách `Session` MCP hiện tại khỏi `Session` Desktop: nếu muốn thay đổi hiển thị tức thời, thiết kế `desktop-ipc` với command queue, mutex trên UI thread, optimistic revision, undo và user confirmation. Không coi việc lưu lại cùng `.rgis` là đồng bộ thời gian thực.

## Gợi ý giai đoạn 2027

- P0: stdio smoke tests, CI, docs, policy deny-by-default.
- P1: CLI read-only remote bridge, authentication, safe schema validation.
- P2: GUI synchronization with explicit user approval and undo.
- P3: Vietnamese tool descriptions, CRS VN-2000 validation, raster/vector provenance, logs, staged release on Windows.

## Nguồn & giấy phép

Dựa trên `opengeos/RustGIS`; phải giữ Apache-2.0 và attribution của mã kế thừa. viRustGIS: tích hợp và Việt hóa bởi dự án xulytiengviet. Đề xuất và tài liệu tích hợp: Long Ngo.
