/// Central place for the backend base URL.
///
/// Running on web (flutter run -d chrome)? The browser runs on the same
/// machine as your backend, so "localhost" works as-is — no changes needed.
///
/// If you later test on a physical phone instead, you'd change this to
/// your PC's local network IP (find it with `ipconfig` on Windows).
class ApiConfig {
  static const String baseUrl = "https://mind-companion-backend-cu25.onrender.com";
}

