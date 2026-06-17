import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class InsightsScreen extends StatefulWidget {
  final String userId;

  const InsightsScreen({super.key, required this.userId});

  @override
  State<InsightsScreen> createState() => _InsightsScreenState();
}

class _InsightsScreenState extends State<InsightsScreen> {
  List<dynamic> _insights = [];
  bool _isLoading = false;
  String _error = '';

  Future<void> _generateInsights() async {
    setState(() {
      _isLoading = true;
      _error = '';
    });

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/insights/generate?user_id=${widget.userId}'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _insights = data;
        });
      } else {
        setState(() {
          _error = 'Failed to generate insights';
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

  Future<void> _loadInsights() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/insights/?user_id=${widget.userId}'),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _insights = data;
        });
      }
    } catch (e) {
      // silent fail for now
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    _loadInsights();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Insights'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadInsights,
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: ElevatedButton.icon(
              onPressed: _isLoading ? null : _generateInsights,
              icon: const Icon(Icons.auto_awesome),
              label: const Text('Generate New Insights'),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 50),
              ),
            ),
          ),
          if (_error.isNotEmpty)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(_error, style: const TextStyle(color: Colors.red)),
            ),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _insights.isEmpty
                    ? const Center(
                        child: Text(
                          "We're still learning about your emotional patterns.\nContinue chatting to unlock personalized insights.",
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.grey),
                        ),
                      )
                    : ListView.builder(
                        itemCount: _insights.length,
                        itemBuilder: (context, index) {
                          final insight = _insights[index];
                          return Card(
                            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    insight['title'] ?? 'Insight',
                                    style: const TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(insight['explanation'] ?? ''),
                                  if (insight['insight_type'] != null)
                                    Padding(
                                      padding: const EdgeInsets.only(top: 8),
                                      child: Chip(
                                        label: Text(insight['insight_type']),
                                        backgroundColor: Colors.teal.shade50,
                                      ),
                                    ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
