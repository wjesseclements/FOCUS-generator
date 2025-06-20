import React from 'react';
import { motion } from 'framer-motion';

const pageVariants = {
  initial: {
    opacity: 0,
    y: 50,
    scale: 0.98,
  },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.6,
      ease: [0.22, 1, 0.36, 1], // Custom easing
      staggerChildren: 0.1,
    },
  },
  exit: {
    opacity: 0,
    y: -50,
    scale: 1.02,
    transition: {
      duration: 0.3,
      ease: [0.22, 1, 0.36, 1],
    },
  },
};

const itemVariants = {
  initial: {
    opacity: 0,
    y: 30,
    scale: 0.95,
  },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: [0.22, 1, 0.36, 1],
    },
  },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

const FloatingElement = ({ children, delay = 0, className = "" }) => (
  <motion.div
    initial={{ opacity: 0, y: 20, scale: 0.9 }}
    animate={{ 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: {
        delay,
        duration: 0.6,
        ease: [0.22, 1, 0.36, 1],
      }
    }}
    whileHover={{ y: -2, transition: { duration: 0.2 } }}
    className={className}
  >
    {children}
  </motion.div>
);

const PageTransition = ({ children, className = "" }) => (
  <motion.div
    variants={pageVariants}
    initial="initial"
    animate="animate"
    exit="exit"
    className={className}
  >
    {children}
  </motion.div>
);

const StaggeredContainer = ({ children, className = "" }) => (
  <motion.div
    variants={staggerContainer}
    initial="initial"
    animate="animate"
    className={className}
  >
    {children}
  </motion.div>
);

const AnimatedItem = ({ children, className = "" }) => (
  <motion.div
    variants={itemVariants}
    className={className}
  >
    {children}
  </motion.div>
);

// Entrance animation for the entire app
const AppEntrance = ({ children }) => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ duration: 0.8, ease: "easeOut" }}
  >
    {children}
  </motion.div>
);

// Sparkle animation for success states
const SparkleAnimation = ({ className = "" }) => (
  <motion.div
    className={`absolute inset-0 pointer-events-none ${className}`}
  >
    {[...Array(6)].map((_, i) => (
      <motion.div
        key={i}
        className="absolute w-1 h-1 bg-yellow-400 rounded-full"
        style={{
          left: `${20 + i * 15}%`,
          top: `${30 + (i % 2) * 40}%`,
        }}
        animate={{
          scale: [0, 1, 0],
          opacity: [0, 1, 0],
          rotate: [0, 180, 360],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          delay: i * 0.2,
          ease: "easeInOut",
        }}
      />
    ))}
  </motion.div>
);

export {
  PageTransition,
  StaggeredContainer,
  AnimatedItem,
  FloatingElement,
  AppEntrance,
  SparkleAnimation,
  pageVariants,
  itemVariants,
};