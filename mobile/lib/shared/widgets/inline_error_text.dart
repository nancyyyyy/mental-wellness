import 'package:flutter/material.dart';

class InlineErrorText extends StatelessWidget {
  final String message;

  const InlineErrorText(this.message, {super.key});

  @override
  Widget build(BuildContext context) {
    if (message.isEmpty) return const SizedBox.shrink();
    final scheme = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        message,
        style: TextStyle(color: scheme.error, fontSize: 13),
      ),
    );
  }
}
