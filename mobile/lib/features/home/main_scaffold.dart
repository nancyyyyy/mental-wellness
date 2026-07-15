import 'package:flutter/material.dart';
import '../chat/chat_screen.dart';
import '../practices/practices_screen.dart';
import '../insights/insights_screen.dart';
import '../../core/auth_service.dart';
import '../../shared/widgets/loading_view.dart';

class MainScaffold extends StatefulWidget {
  const MainScaffold({super.key});

  @override
  State<MainScaffold> createState() => _MainScaffoldState();
}

class _MainScaffoldState extends State<MainScaffold> {
  int _currentIndex = 0;
  String? _userId;

  @override
  void initState() {
    super.initState();
    _loadUserId();
  }

  Future<void> _loadUserId() async {
    final userId = await AuthService.getUserId();
    setState(() {
      _userId = userId ?? 'demo-user';
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_userId == null) {
      return const Scaffold(
        body: LoadingView(),
      );
    }

    final screens = [
      ChatScreen(userId: _userId),
      PracticesScreen(userId: _userId!),
      InsightsScreen(userId: _userId!),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.chat_bubble_outline),
            activeIcon: Icon(Icons.chat_bubble),
            label: 'Chat',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.self_improvement_outlined),
            activeIcon: Icon(Icons.self_improvement),
            label: 'Practices',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.insights_outlined),
            activeIcon: Icon(Icons.insights),
            label: 'Insights',
          ),
        ],
      ),
    );
  }
}
