import React from 'react';
import { motion } from 'framer-motion';

// Hover card with magnetic effect
export const MagneticCard = ({ children, className = "", ...props }) => {
  return (
    <motion.div
      className={className}
      whileHover={{ 
        y: -1,
        transition: { duration: 0.2, ease: "easeOut" }
      }}
      {...props}
    >
      {children}
    </motion.div>
  );
};

// Button with ripple effect
export const RippleButton = ({ children, onClick, className = "", ...props }) => {
  const [ripples, setRipples] = React.useState([]);

  const createRipple = (event) => {
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    const newRipple = {
      x,
      y,
      size,
      id: Date.now(),
    };

    setRipples(prev => [...prev, newRipple]);
    
    // Remove ripple after animation
    setTimeout(() => {
      setRipples(prev => prev.filter(ripple => ripple.id !== newRipple.id));
    }, 600);

    if (onClick) onClick(event);
  };

  return (
    <motion.button
      className={`relative overflow-hidden ${className}`}
      onClick={createRipple}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      {...props}
    >
      {children}
      {ripples.map(ripple => (
        <motion.span
          key={ripple.id}
          className="absolute bg-white/30 rounded-full pointer-events-none"
          style={{
            left: ripple.x,
            top: ripple.y,
            width: ripple.size,
            height: ripple.size,
          }}
          initial={{ scale: 0, opacity: 1 }}
          animate={{ scale: 2, opacity: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        />
      ))}
    </motion.button>
  );
};

// Floating action button
export const FloatingButton = ({ children, className = "", ...props }) => (
  <motion.button
    className={`fixed bottom-8 right-8 z-50 ${className}`}
    initial={{ scale: 0, opacity: 0 }}
    animate={{ scale: 1, opacity: 1 }}
    transition={{ delay: 1, type: "spring", stiffness: 200, damping: 20 }}
    whileHover={{ 
      scale: 1.1,
      rotate: 5,
      transition: { duration: 0.2 }
    }}
    whileTap={{ scale: 0.9 }}
    {...props}
  >
    {children}
  </motion.button>
);

// Parallax element
export const ParallaxElement = ({ children, offset = 50, className = "" }) => {
  const [scrollY, setScrollY] = React.useState(0);

  React.useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <motion.div
      className={className}
      style={{
        y: scrollY * offset * 0.01,
      }}
    >
      {children}
    </motion.div>
  );
};

// Bouncing icon
export const BouncingIcon = ({ children, delay = 0, className = "" }) => (
  <motion.div
    className={className}
    animate={{
      y: [0, -10, 0],
    }}
    transition={{
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut",
      delay,
    }}
  >
    {children}
  </motion.div>
);

// Typing animation
export const TypingText = ({ text, className = "", delay = 0 }) => {
  const [displayText, setDisplayText] = React.useState('');
  const [currentIndex, setCurrentIndex] = React.useState(0);

  React.useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, 50 + delay);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, text, delay]);

  return (
    <span className={className}>
      {displayText}
      <motion.span
        animate={{ opacity: [1, 0] }}
        transition={{ duration: 0.8, repeat: Infinity }}
        className="inline-block w-0.5 h-5 bg-current ml-1"
      />
    </span>
  );
};

// Pulse effect
export const PulseEffect = ({ children, className = "", ...props }) => (
  <motion.div
    className={`relative ${className}`}
    {...props}
  >
    {children}
    <motion.div
      className="absolute inset-0 rounded-full bg-primary/20"
      animate={{
        scale: [1, 1.2, 1],
        opacity: [0.5, 0, 0.5],
      }}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    />
  </motion.div>
);

// Progress indicator
export const ProgressRing = ({ progress, size = 60, strokeWidth = 4, className = "" }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <div className={`relative ${className}`}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="none"
          className="text-gray-200 dark:text-gray-700"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          className="text-primary"
          initial={{ strokeDasharray: circumference, strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
          style={{
            strokeDasharray: circumference,
            strokeDashoffset: offset,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-sm font-semibold">{Math.round(progress)}%</span>
      </div>
    </div>
  );
};