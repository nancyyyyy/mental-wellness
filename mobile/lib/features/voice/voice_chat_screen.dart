import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class VoiceChatScreen extends StatefulWidget {
  const VoiceChatScreen({super.key});

  @override
  State<VoiceChatScreen> createState() => _VoiceChatScreenState();
}

class _VoiceChatScreenState extends State<VoiceChatScreen> {
  final SpeechToText _speechToText = SpeechToText();
  final FlutterTts _flutterTts = FlutterTts();
  
  bool _isListening = false;
  bool _isSpeaking = false;
  bool _isProcessing = false;
  String _lastWords = '';
  String _aiResponse = '';

  @override
  void initState() {
    super.initState();
    _initSpeech();
    _initTts();
  }

  void _initSpeech() async {
    await _speechToText.initialize();
    setState(() {});
  }

  void _initTts() async {
    await _flutterTts.setLanguage("en-US");
    await _flutterTts.setSpeechRate(0.5);
    await _flutterTts.setVolume(1.0);
    await _flutterTts.setPitch(1.0);
  }

  Future<void> _startListening() async {
    if (!_isListening) {
      bool available = await _speechToText.initialize();
      if (available) {
        setState(() => _isListening = true);
        _speechToText.listen(
          onResult: (result) {
            setState(() {
              _lastWords = result.recognizedWords;
            });
          },
        );
      }
    }
  }

  Future<void> _stopListening() async {
    await _speechToText.stop();
    setState(() => _isListening = false);
    
    if (_lastWords.isNotEmpty) {
      await _sendToBackend(_lastWords);
    }
  }

  Future<void> _sendToBackend(String text) async {
    setState(() {
      _isProcessing = true;
      _aiResponse = '';
    });

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/chat/message'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          "content": text,
          "user_id": "voice-user-1"
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final aiText = data['response'] ?? "I'm here with you.";
        
        setState(() {
          _aiResponse = aiText;
          _isProcessing = false;
        });

        // Speak the response
        await _speak(aiText);
      }
    } catch (e) {
      setState(() {
        _aiResponse = "Sorry, I couldn't connect right now.";
        _isProcessing = false;
      });
    } finally {
      setState(() {
        _isProcessing = false;
      });
    }
  }

  Future<void> _speak(String text) async {
    setState(() => _isSpeaking = true);
    await _flutterTts.speak(text);
    setState(() => _isSpeaking = false);
  }

  Future<void> _stopSpeaking() async {
    await _flutterTts.stop();
    setState(() => _isSpeaking = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voice Companion'),
        backgroundColor: Colors.teal,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            const SizedBox(height: 40),
            
            // Status
            Text(
              _isListening 
                  ? "🎤 Listening..." 
                  : _isSpeaking 
                      ? "🔊 Speaking..." 
                      : _isProcessing 
                          ? "🤔 Thinking..." 
                          : "Tap the mic to speak",
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w500),
            ),
            
            const SizedBox(height: 30),
            
            // User speech
            if (_lastWords.isNotEmpty)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  "You said: $_lastWords",
                  style: const TextStyle(fontSize: 16),
                ),
              ),
            
            const SizedBox(height: 20),
            
            // AI Response
            if (_aiResponse.isNotEmpty)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.teal[50],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  "Companion: $_aiResponse",
                  style: const TextStyle(fontSize: 16),
                ),
              ),
            
            const Spacer(),
            
            // Mic Button
            GestureDetector(
              onTapDown: (_) => _startListening(),
              onTapUp: (_) => _stopListening(),
              child: Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: _isListening ? Colors.red : Colors.teal,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black26,
                      blurRadius: 10,
                      spreadRadius: 2,
                    )
                  ],
                ),
                child: Icon(
                  _isListening ? Icons.mic : Icons.mic_none,
                  color: Colors.white,
                  size: 60,
                ),
              ),
            ),
            
            const SizedBox(height: 20),
            
            Text(
              _isListening ? "Release to send" : "Hold to speak",
              style: TextStyle(color: Colors.grey[600]),
            ),
            
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }
}