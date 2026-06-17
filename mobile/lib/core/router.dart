import 'package:go_router/go_router.dart';
import '../features/auth/welcome_screen.dart';
import '../features/auth/login_screen.dart';
import '../features/auth/register_screen.dart';
import '../features/home/main_scaffold.dart';
import '../features/voice/voice_chat_screen.dart';
import '../core/auth_service.dart';

final appRouter = GoRouter(
  initialLocation: '/',
  redirect: (context, state) async {
    final loggedIn = await AuthService.isLoggedIn();
    final goingToAuth = state.uri.toString().startsWith('/login') ||
        state.uri.toString().startsWith('/register') ||
        state.uri.toString() == '/';

    if (!loggedIn && !goingToAuth) {
      return '/';
    }
    if (loggedIn && goingToAuth) {
      return '/chat';
    }
    return null;
  },
  routes: [
    GoRoute(path: '/', builder: (context, state) => const WelcomeScreen()),
    GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
    GoRoute(path: '/register', builder: (context, state) => const RegisterScreen()),
    GoRoute(path: '/chat', builder: (context, state) => const MainScaffold()),
    GoRoute(path: '/voice', builder: (context, state) => const VoiceChatScreen()),
  ],
);