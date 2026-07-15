import 'package:flutter/material.dart';
import '../models/chat_message.dart';

class MessageBubble extends StatelessWidget {
  final ChatMessage message;
  final VoidCallback? onRetry;

  const MessageBubble({super.key, required this.message, this.onRetry});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final isUser = message.role == ChatRole.user;

    Color background;
    Color foreground;
    if (message.isError) {
      background = scheme.errorContainer;
      foreground = scheme.onErrorContainer;
    } else if (isUser) {
      background = scheme.secondaryContainer;
      foreground = scheme.onSecondaryContainer;
    } else {
      background = scheme.primaryContainer;
      foreground = scheme.onPrimaryContainer;
    }

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Column(
        crossAxisAlignment:
            isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.78,
            ),
            margin: const EdgeInsets.symmetric(vertical: 4),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: background,
              borderRadius: BorderRadius.only(
                topLeft: const Radius.circular(16),
                topRight: const Radius.circular(16),
                bottomLeft: Radius.circular(isUser ? 16 : 4),
                bottomRight: Radius.circular(isUser ? 4 : 16),
              ),
            ),
            child: Text(
              message.content,
              style: TextStyle(fontSize: 15, color: foreground),
            ),
          ),
          if (message.isError && onRetry != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: TextButton(
                onPressed: onRetry,
                style: TextButton.styleFrom(
                  padding: EdgeInsets.zero,
                  minimumSize: const Size(0, 0),
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: const Text('Retry'),
              ),
            ),
        ],
      ),
    );
  }
}
