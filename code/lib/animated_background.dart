import 'package:flutter/material.dart';
import 'dart:math' show sin, cos, pi;

/// $REQ_ANIMATED_BG_001: Background Source Image
/// $REQ_ANIMATED_BG_002: Tiled Background Coverage
/// $REQ_ANIMATED_BG_003: Scroll Direction Formula
/// $REQ_ANIMATED_BG_004: Scroll Angle
/// $REQ_ANIMATED_BG_005: Scroll Speed
/// $REQ_ANIMATED_BG_006: Seamless Wrapping
/// $REQ_ANIMATED_BG_007: Continuous Animation
class AnimatedBackground extends StatefulWidget {
  const AnimatedBackground({super.key});

  @override
  State<AnimatedBackground> createState() => _AnimatedBackgroundState();
}

class _AnimatedBackgroundState extends State<AnimatedBackground>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  // $REQ_ANIMATED_BG_004: Scroll angle MUST be 45 degrees
  final double scrollAngle = 45.0;

  // $REQ_ANIMATED_BG_005: Scroll speed MUST be 50 pixels per second
  final double scrollSpeed = 50.0;

  @override
  void initState() {
    super.initState();
    // $REQ_ANIMATED_BG_007: Continuous animation
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(days: 365), // Effectively infinite
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        // Calculate elapsed time in seconds
        final elapsed = _controller.duration!.inMilliseconds * _controller.value / 1000.0;

        // $REQ_ANIMATED_BG_003: Scroll Direction Formula
        // dx = s × sin(θ) (horizontal displacement per second)
        // dy = −s × cos(θ) (vertical displacement per second)
        final radians = scrollAngle * pi / 180.0;
        final dx = scrollSpeed * sin(radians) * elapsed;
        final dy = -scrollSpeed * cos(radians) * elapsed;

        return _TiledBackground(
          offsetX: dx,
          offsetY: dy,
        );
      },
    );
  }
}

/// Custom painter that tiles the background image with wrapping
class _TiledBackground extends StatelessWidget {
  final double offsetX;
  final double offsetY;

  const _TiledBackground({
    required this.offsetX,
    required this.offsetY,
  });

  @override
  Widget build(BuildContext context) {
    // $REQ_ANIMATED_BG_001: Background MUST use extart/bg.jpg as the source image
    // $REQ_ANIMATED_BG_006: Seamless wrapping using Transform.translate
    return Transform.translate(
      offset: Offset(
        offsetX % 200, // Wrap at 200px (image width)
        offsetY % 200, // Wrap at 200px (image height)
      ),
      child: Container(
        decoration: BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/bg.jpg'), // Copied from extart/bg.jpg
            // $REQ_ANIMATED_BG_002: Tiled to fill viewport completely
            repeat: ImageRepeat.repeat,
            alignment: Alignment.topLeft,
          ),
        ),
      ),
    );
  }
}
