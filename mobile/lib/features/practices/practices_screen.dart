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
  bool _isLoading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _fetchPractices();
  }

  Future<void> _fetchPractices() async {
    setState(() {
      _isLoading = true;
      _error = '';
    });

    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/practices/recommend?user_id=${widget.userId}&limit=4'),
      );

      if (response.statusCode == 200) {
        setState(() {
          _practices = jsonDecode(response.body);
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
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Practices & Healing'),
        backgroundColor: Colors.teal,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error.isNotEmpty
              ? Center(child: Text(_error))
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
                              practice['title'] ?? 'Practice',
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Colors.teal,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              practice['why_it_helps'] ?? '',
                              style: const TextStyle(fontSize: 15),
                            ),
                            const SizedBox(height: 12),
                            const Text(
                              'How to practice:',
                              style: TextStyle(fontWeight: FontWeight.w600),
                            ),
                            const SizedBox(height: 6),
                            ...((practice['steps'] as List<dynamic>?) ?? [])
                                .map((step) => Padding(
                                      padding: const EdgeInsets.only(bottom: 4),
                                      child: Text('• $step'),
                                    )),
                            const SizedBox(height: 12),
                            Row(
                              children: [
                                Chip(
                                  label: Text(practice['duration'] ?? '5 min'),
                                  backgroundColor: Colors.teal.shade50,
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    practice['expected_benefit'] ?? '',
                                    style: const TextStyle(fontSize: 14),
                                  ),
                                ),
                              ],
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