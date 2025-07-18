import React from 'react';
import { motion } from 'framer-motion';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import { Button } from './button';

const DarkModeToggle = ({ className = "" }) => {
  const { isDarkMode, toggleDarkMode, isLoaded } = useTheme();

  if (!isLoaded) return null; // Prevent hydration mismatch

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.5 }}
      className={className}
    >
      <Button
        variant="glass"
        size="icon"
        onClick={toggleDarkMode}
        className="relative overflow-hidden group bg-white/10 dark:bg-black/20 backdrop-blur-md border border-white/20 dark:border-white/10 hover:border-primary/50 transition-all duration-300"
        aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
      >
        <motion.div
          key={isDarkMode ? 'moon' : 'sun'}
          initial={{ y: -20, opacity: 0, rotate: -90 }}
          animate={{ y: 0, opacity: 1, rotate: 0 }}
          exit={{ y: 20, opacity: 0, rotate: 90 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          className="absolute inset-0 flex items-center justify-center"
        >
          {isDarkMode ? (
            <Moon className="h-4 w-4 text-blue-100 group-hover:text-white transition-colors" />
          ) : (
            <Sun className="h-4 w-4 text-yellow-600 group-hover:text-yellow-500 transition-colors" />
          )}
        </motion.div>
        
        {/* Glow effect */}
        <div className={`absolute inset-0 rounded-full transition-opacity duration-300 ${
          isDarkMode 
            ? 'bg-blue-500/20 group-hover:bg-blue-500/30' 
            : 'bg-yellow-500/20 group-hover:bg-yellow-500/30'
        }`} />
      </Button>
    </motion.div>
  );
};

export default DarkModeToggle;