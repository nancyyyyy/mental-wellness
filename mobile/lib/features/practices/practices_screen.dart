import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class PracticesScreen extends StatefulWidget {
  final String userId;

  const PracticesScreen({super.key, required this.userId});

  @override
  State<PracticesScreen> createState() => _PracticesScreenState();
}

class _PracticesScreenState extends State<PracticesScreen> {
  List<dynamic> _practices = [];
  bool _isLoading = false;
  String _error = '';

  Future<void> _loadPractices() async {
    setState(() {
      _isLoading = true;
      _error = '';
    });

    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/practices/recommendations?user_id=${widget.userId}'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _practices = data;
        });
      } else {
        setState(() {
          _error = 'Failed to load practices';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Connection error';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    _loadPractices();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Practices'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadPractices,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error.isNotEmpty
              ? Center(child: Text(_error, style: const TextStyle(color: Colors.red)))
              : _practices.isEmpty
                  ? const Center(
                      child: Text(
                        'No personalized practices yet.\nTry chatting more to unlock recommendations.',
                        textAlign: TextAlign.center,
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _practices.length,
                      itemBuilder: (context, index) {
                        final practice = _practices[index];
                        return Card(
                          margin: const EdgeInsets.only(bottom: 16),
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  practice['name'] ?? 'Practice',
                                  style: const TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  practice['why'] ?? '',
                                  style: const TextStyle(fontSize: 15),
                                ),
                                const SizedBox(height: 12),
                                const Text(
                                  'How to practice:',
                                  style: TextStyle(fontWeight: FontWeight.w600),
                                ),
                                const SizedBox(height: 4),
                                Text(practice['how'] ?? ''),
                                const SizedBox(height: 12),
                                Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: Colors.teal.shade50,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Row(
                                    children: [
                                      const Icon(Icons.check_circle, color: Colors.teal, size: 20),
                                      const SizedBox(width: 8),
                                      Expanded(
                                        child: Text(
                                          practice['benefit'] ?? '',
                                          style: const TextStyle(color: Colors.teal),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
    );
  }
}
