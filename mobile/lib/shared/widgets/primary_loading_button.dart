import 'package:flutter/material.dart';

class PrimaryLoadingButton extends StatelessWidget {
  final bool isLoading;
  final VoidCallback? onPressed;
  final String label;

  const PrimaryLoadingButton({
    super.key,
    required this.isLoading,
    required this.onPressed,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return ElevatedButton(
      onPressed: isLoading ? null : onPressed,
      child: isLoading
          ? SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2.2,
                color: scheme.onPrimary,
              ),
            )
          : Text(label),
    );
  }
}
