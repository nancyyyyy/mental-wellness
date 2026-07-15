import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Warm serif (Literata) for headings, system sans for body/labels.
class AppTextTheme {
  AppTextTheme._();

  static TextTheme build(ColorScheme scheme) {
    final base = ThemeData(brightness: scheme.brightness).textTheme;

    TextStyle serif(double size, FontWeight weight, Color color) {
      return GoogleFonts.literata(
        fontSize: size,
        fontWeight: weight,
        color: color,
      );
    }

    return base.copyWith(
      displayLarge: serif(40, FontWeight.w600, scheme.onSurface),
      displayMedium: serif(32, FontWeight.w600, scheme.onSurface),
      displaySmall: serif(28, FontWeight.w600, scheme.onSurface),
      headlineLarge: serif(26, FontWeight.w600, scheme.onSurface),
      headlineMedium: serif(23, FontWeight.w600, scheme.onSurface),
      headlineSmall: serif(20, FontWeight.w600, scheme.onSurface),
      titleLarge: serif(18, FontWeight.w600, scheme.onSurface),
      titleMedium: base.titleMedium?.copyWith(
        color: scheme.onSurface,
        fontWeight: FontWeight.w600,
      ),
      titleSmall: base.titleSmall?.copyWith(
        color: scheme.onSurface,
        fontWeight: FontWeight.w600,
      ),
      bodyLarge: base.bodyLarge?.copyWith(color: scheme.onSurface),
      bodyMedium: base.bodyMedium?.copyWith(color: scheme.onSurface),
      bodySmall: base.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
      labelLarge: base.labelLarge?.copyWith(
        color: scheme.onSurface,
        fontWeight: FontWeight.w600,
      ),
      labelMedium: base.labelMedium?.copyWith(color: scheme.onSurfaceVariant),
      labelSmall: base.labelSmall?.copyWith(color: scheme.onSurfaceVariant),
    );
  }
}
