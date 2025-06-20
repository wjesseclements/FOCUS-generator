import React from "react";
import { motion } from "framer-motion";

const HeroSection = () => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="w-full py-20 px-4 text-center relative"
    >
      {/* Completely transparent - no background at all */}
      <motion.h1 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.6 }}
        className="text-6xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-gray-900 via-primary to-secondary bg-clip-text text-transparent dark:from-white dark:via-blue-200 dark:to-purple-200"
      >
        FOCUS CUR Generator
      </motion.h1>
      <motion.p 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.6 }}
        className="text-xl md:text-2xl max-w-3xl mx-auto text-gray-700 dark:text-gray-300 leading-relaxed"
      >
        Quickly generate synthetic FOCUS-conformed Cost and Usage Reports for
        your testing and FinOps needs.
      </motion.p>
      
      {/* Decorative elements */}
      <motion.div
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.8, duration: 0.5 }}
        className="mt-8 flex justify-center space-x-2"
      >
        {[...Array(3)].map((_, i) => (
          <div
            key={i}
            className="w-2 h-2 bg-gradient-to-r from-primary to-secondary rounded-full animate-pulse"
            style={{ animationDelay: `${i * 0.3}s` }}
          />
        ))}
      </motion.div>
    </motion.div>
  );
};

export default HeroSection;