import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../core/auth_service.dart';
import '../../core/api_config.dart';
import '../../shared/models/chat_message.dart';
import '../../shared/widgets/message_bubble.dart';
import '../../shared/widgets/typing_indicator.dart';

class ChatScreen extends StatefulWidget {
  final String? userId;

  const ChatScreen({super.key, this.userId});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<ChatMessage> _messages = [
    ChatMessage(
      role: ChatRole.companion,
      content: "Hello! I'm your Mind Companion. How are you feeling today?",
    ),
  ];
  bool _isLoading = false;
  late String userId;
  int? _conversationId;

  @override
  void initState() {
    super.initState();
    userId = widget.userId ?? "demo-user";
  }

  Future<void> _sendMessage([String? retryText]) async {
    final userMessage = retryText ?? _controller.text.trim();
    if (userMessage.isEmpty) return;

    setState(() {
      _messages.add(ChatMessage(role: ChatRole.user, content: userMessage));
      _isLoading = true;
    });
    if (retryText == null) _controller.clear();

    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}/chat/message'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          "content": userMessage,
          "user_id": userId,
          "conversation_id": _conversationId,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final aiResponse = data['response'] ?? "I'm here to support you.";
        setState(() {
          _messages.add(
              ChatMessage(role: ChatRole.companion, content: aiResponse));
          _conversationId = data['conversation_id'] ?? _conversationId;
        });
      } else {
        setState(() {
          _messages.add(ChatMessage(
            role: ChatRole.companion,
            content: "Sorry, I'm having trouble responding.",
            isError: true,
          ));
        });
      }
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          role: ChatRole.companion,
          content: "Connection error. Is the backend running?",
          isError: true,
        ));
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mind Companion'),
        actions: [
          IconButton(
            icon: const Icon(Icons.mic),
            onPressed: () => context.go('/voice'),
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () async {
              await AuthService.logout();
              if (context.mounted) context.go('/login');
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length + (_isLoading ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == _messages.length) {
                  return const TypingIndicator();
                }
                final message = _messages[index];
                return MessageBubble(
                  message: message,
                  onRetry: message.isError
                      ? () {
                          final lastUser = _messages.lastWhere(
                            (m) => m.role == ChatRole.user,
                            orElse: () => message,
                          );
                          _sendMessage(lastUser.content);
                        }
                      : null,
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    decoration: const InputDecoration(
                      hintText: "Type your message...",
                    ),
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: Icon(Icons.send,
                      color: Theme.of(context).colorScheme.primary),
                  onPressed: _isLoading ? null : () => _sendMessage(),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
