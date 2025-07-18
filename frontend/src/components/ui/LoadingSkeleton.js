import React from 'react';
import { motion } from 'framer-motion';

const SkeletonCard = ({ className = "", animated = true }) => {
  const baseClasses = "bg-gray-200 dark:bg-gray-700 rounded-2xl";
  
  if (animated) {
    return (
      <motion.div
        className={`${baseClasses} ${className}`}
        animate={{
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    );
  }
  
  return <div className={`${baseClasses} ${className} animate-pulse`} />;
};

const LoadingSkeleton = ({ variant = "cards" }) => {
  if (variant === "cards") {
    return (
      <div className="space-y-8">
        {/* Profile Selection Skeleton */}
        <div className="text-center">
          <SkeletonCard className="h-8 w-64 mx-auto mb-6" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="glass-card p-6"
              >
                <div className="flex items-center space-x-4">
                  <SkeletonCard className="w-14 h-14 rounded-xl" />
                  <div className="flex-1 space-y-2">
                    <SkeletonCard className="h-5 w-3/4" />
                    <SkeletonCard className="h-4 w-full" />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Distribution Selection Skeleton */}
        <div className="text-center">
          <SkeletonCard className="h-8 w-48 mx-auto mb-6" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + i * 0.1 }}
                className="glass-card p-4 text-center"
              >
                <SkeletonCard className="w-12 h-12 rounded-xl mx-auto mb-3" />
                <SkeletonCard className="h-4 w-24 mx-auto" />
              </motion.div>
            ))}
          </div>
        </div>

        {/* Row Count Skeleton */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="max-w-lg mx-auto"
        >
          <div className="glass-card p-8">
            <SkeletonCard className="h-6 w-32 mx-auto mb-6" />
            <SkeletonCard className="h-4 w-48 mx-auto mb-4" />
            <SkeletonCard className="h-2 w-full rounded-full mb-4" />
            <SkeletonCard className="h-10 w-20 mx-auto" />
          </div>
        </motion.div>

        {/* Button Skeleton */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="text-center"
        >
          <SkeletonCard className="h-12 w-48 mx-auto rounded-xl" />
        </motion.div>
      </div>
    );
  }

  if (variant === "generating") {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-md mx-auto"
      >
        <div className="glass-card p-8 text-center">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              rotate: [0, 180, 360],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            className="w-16 h-16 mx-auto mb-6 rounded-full bg-gradient-primary"
          />
          <SkeletonCard className="h-6 w-48 mx-auto mb-4" />
          <SkeletonCard className="h-4 w-64 mx-auto mb-2" />
          <SkeletonCard className="h-4 w-32 mx-auto" />
          
          {/* Progress Bar */}
          <div className="mt-6 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <motion.div
              className="bg-gradient-primary h-2 rounded-full"
              animate={{
                width: ["0%", "70%", "100%"],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut",
              }}
            />
          </div>
        </div>
      </motion.div>
    );
  }

  return null;
};

export { LoadingSkeleton, SkeletonCard };