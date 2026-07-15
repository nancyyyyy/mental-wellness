enum ChatRole { user, companion }

class ChatMessage {
  final ChatRole role;
  final String content;
  final DateTime timestamp;
  final bool isError;

  ChatMessage({
    required this.role,
    required this.content,
    DateTime? timestamp,
    this.isError = false,
  }) : timestamp = timestamp ?? DateTime.now();
}
