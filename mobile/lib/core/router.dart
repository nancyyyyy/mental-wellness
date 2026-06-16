import 'package:go_router/go_router.dart';
import '../features/chat/chat_screen.dart';
import '../features/voice/voice_chat_screen.dart';
import '../features/practices/practices_screen.dart';

final appRouter = GoRouter(
  initialLocation: '/chat',
  routes: [
    GoRoute(path: '/chat', builder: (context, state) => const ChatScreen()),
    GoRoute(path: '/voice', builder: (context, state) => const VoiceChatScreen()),
    GoRoute(path: '/practices', builder: (context, state) => const PracticesScreen(userId: 'demo-user')),
  ],
);