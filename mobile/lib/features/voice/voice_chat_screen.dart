import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

class VoiceChatScreen extends StatefulWidget {
  const VoiceChatScreen({super.key});

  @override
  State<VoiceChatScreen> createState() => _VoiceChatScreenState();
}

class _VoiceChatScreenState extends State<VoiceChatScreen> {
  final SpeechToText _speechToText = SpeechToText();
  final FlutterTts _flutterTts = FlutterTts();

  bool _isCallActive = false;
  bool _isListening = false;
  bool _isSpeaking = false;
  bool _isProcessing = false;

  String _lastWords = '';
  String _aiResponse = '';
  String _statusText = 'Tap "Start Call" to begin';

  Timer? _silenceTimer;

  @override
  void initState() {
    super.initState();
    _initSpeech();
    _initTts();
  }

  void _initSpeech() async {
    await _speechToText.initialize();
  }

  void _initTts() async {
    await _flutterTts.setLanguage("en-US");
    await _flutterTts.setSpeechRate(0.48);
    await _flutterTts.setVolume(1.0);
    await _flutterTts.setPitch(1.0);

    _flutterTts.setCompletionHandler(() {
      if (_isCallActive) {
        _startListening();
      }
    });
  }

  Future<void> _startCall() async {
    setState(() {
      _isCallActive = true;
      _statusText = 'Listening...';
      _lastWords = '';
      _aiResponse = '';
    });
    await _startListening();
  }

  Future<void> _endCall() async {
    setState(() {
      _isCallActive = false;
      _isListening = false;
      _isSpeaking = false;
      _isProcessing = false;
      _statusText = 'Call ended';
    });
    await _speechToText.stop();
    await _flutterTts.stop();
    _silenceTimer?.cancel();
  }

  Future<void> _startListening() async {
    if (!_isCallActive || _isListening || _isSpeaking || _isProcessing) return;

    bool available = await _speechToText.initialize();
    if (!available) return;

    setState(() {
      _isListening = true;
      _lastWords = '';
      _statusText = 'Listening...';
    });

    _silenceTimer?.cancel();

    _speechToText.listen(
      onResult: (result) {
        setState(() {
          _lastWords = result.recognizedWords;
        });

        // Reset silence timer whenever user speaks
        _silenceTimer?.cancel();
        _silenceTimer = Timer(const Duration(seconds: 2), () {
          if (_isListening && _lastWords.isNotEmpty) {
            _stopListeningAndSend();
          }
        });
      },
      listenFor: const Duration(seconds: 30),
      pauseFor: const Duration(seconds: 2),
    );
  }

  Future<void> _stopListeningAndSend() async {
    await _speechToText.stop();
    setState(() {
      _isListening = false;
    });
    _silenceTimer?.cancel();

    if (_lastWords.trim().isNotEmpty) {
      await _sendToBackend(_lastWords.trim());
    } else {
      // If no speech detected, start listening again
      if (_isCallActive) {
        await _startListening();
      }
    }
  }

  Future<void> _sendToBackend(String text) async {
    setState(() {
      _isProcessing = true;
      _statusText = 'Thinking...';
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
          _statusText = 'Speaking...';
        });

        await _speak(aiText);
      }
    } catch (e) {
      setState(() {
        _aiResponse = "Sorry, connection issue.";
        _isProcessing = false;
      });
      if (_isCallActive) {
        await Future.delayed(const Duration(seconds: 1));
        await _startListening();
      }
    }
  }

  Future<void> _speak(String text) async {
    setState(() => _isSpeaking = true);
    await _flutterTts.speak(text);
  }

  @override
  void dispose() {
    _speechToText.stop();
    _flutterTts.stop();
    _silenceTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Voice Call'),
        backgroundColor: Colors.teal,
        actions: [
          if (_isCallActive)
            TextButton(
              onPressed: _endCall,
              child: const Text('End Call', style: TextStyle(color: Colors.white)),
            ),
        ],
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Status
              Text(
                _statusText,
                style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w500),
              ),
              const SizedBox(height: 40),

              // Visual indicator
              Container(
                width: 160,
                height: 160,
                decoration: BoxDecoration(
                  color: _isListening
                      ? Colors.red.shade100
                      : _isSpeaking
                          ? Colors.teal.shade100
                          : Colors.grey.shade200,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  _isListening
                      ? Icons.mic
                      : _isSpeaking
                          ? Icons.volume_up
                          : Icons.mic_none,
                  size: 80,
                  color: _isListening
                      ? Colors.red
                      : _isSpeaking
                          ? Colors.teal
                      : Colors.grey,
                ),
              ),

              const SizedBox(height: 30),

              // Last spoken text
              if (_lastWords.isNotEmpty)
                Text(
                  "You: $_lastWords",
                  style: const TextStyle(fontSize: 16, color: Colors.black87),
                  textAlign: TextAlign.center,
                ),

              const SizedBox(height: 16),

              // AI Response
              if (_aiResponse.isNotEmpty)
                Text(
                  "Companion: $_aiResponse",
                  style: const TextStyle(fontSize: 16, color: Colors.teal),
                  textAlign: TextAlign.center,
                ),

              const Spacer(),

              // Start / End Call Button
              if (!_isCallActive)
                ElevatedButton.icon(
                  onPressed: _startCall,
                  icon: const Icon(Icons.call),
                  label: const Text('Start Voice Call'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.teal,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 16),
                    textStyle: const TextStyle(fontSize: 18),
                  ),
                )
              else
                Text(
                  _isListening
                      ? "Listening... (Speak naturally)"
                      : _isSpeaking
                          ? "Speaking..."
                          : "Processing...",
                  style: const TextStyle(fontSize: 16, color: Colors.grey),
                ),

              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }
}