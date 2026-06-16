import 'package:go_router/go_router.dart';
import '../features/auth/login_screen.dart';
import '../features/auth/register_screen.dart';
import '../features/chat/chat_screen.dart';
import '../features/voice/voice_chat_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/login',
  routes: [
    GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
    GoRoute(path: '/register', builder: (context, state) => const RegisterScreen()),
    GoRoute(
      path: '/chat',
      builder: (context, state) {
        final extra = state.extra as Map<String, dynamic>?;
        final userId = extra?['userId'] as String?;
        return ChatScreen(userId: userId);
      },
    ),
    GoRoute(path: '/voice', builder: (context, state) => const VoiceChatScreen()),
  ],
);