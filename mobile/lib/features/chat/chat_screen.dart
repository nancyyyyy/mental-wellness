import 'package:flutter/material.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _controller = TextEditingController();
  final List<String> _messages = ["Hello! How are you feeling today?"];

  void _send() {
    if (_controller.text.isEmpty) return;
    setState(() {
      _messages.add("You: ${_controller.text}");
      _messages.add("Companion: Thank you for sharing. I'm here with you.");
    });
    _controller.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Chat')),
      body: Column(
        children: [
          Expanded(child: ListView.builder(itemCount: _messages.length, itemBuilder: (c, i) => ListTile(title: Text(_messages[i])))),
          Padding(
            padding: const EdgeInsets.all(8),
            child: Row(children: [
              Expanded(child: TextField(controller: _controller)),
              IconButton(icon: const Icon(Icons.send), onPressed: _send),
            ]),
          ),
        ],
      ),
    );
  }
}