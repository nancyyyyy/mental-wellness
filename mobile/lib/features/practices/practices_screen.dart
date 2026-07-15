import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../core/api_config.dart';
import '../../shared/widgets/loading_view.dart';
import '../../shared/widgets/error_view.dart';
import '../../shared/widgets/empty_state_view.dart';

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
        Uri.parse('${ApiConfig.baseUrl}/practices/recommendations?user_id=${widget.userId}'),
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
    final scheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

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
          ? const LoadingView()
          : _error.isNotEmpty
              ? ErrorView(message: _error, onRetry: _loadPractices)
              : _practices.isEmpty
                  ? const EmptyStateView(
                      message:
                          'No personalized practices yet.\nTry chatting more to unlock recommendations.',
                      icon: Icons.self_improvement_outlined,
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
                                  style: textTheme.titleLarge,
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  practice['why'] ?? '',
                                  style: textTheme.bodyMedium,
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  'How to practice:',
                                  style: textTheme.labelLarge,
                                ),
                                const SizedBox(height: 4),
                                Text(practice['how'] ?? '',
                                    style: textTheme.bodyMedium),
                                const SizedBox(height: 12),
                                Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: scheme.secondaryContainer,
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Row(
                                    children: [
                                      Icon(Icons.check_circle,
                                          color: scheme.onSecondaryContainer,
                                          size: 20),
                                      const SizedBox(width: 8),
                                      Expanded(
                                        child: Text(
                                          practice['benefit'] ?? '',
                                          style: TextStyle(
                                              color:
                                                  scheme.onSecondaryContainer),
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
