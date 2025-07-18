import React from "react";
import { motion } from "framer-motion";
import { cn } from "../../lib/utils.js";

export const Tabs = ({ children, defaultValue, className, ...props }) => {
  const [activeTab, setActiveTab] = React.useState(defaultValue);

  const childrenWithProps = React.Children.map(children, child => {
    if (!React.isValidElement(child)) return child;
    
    return React.cloneElement(child, {
      activeTab,
      setActiveTab
    });
  });

  return (
    <div className={cn("w-full", className)} {...props}>
      {childrenWithProps}
    </div>
  );
};

export const TabsList = ({ children, className, activeTab, setActiveTab, ...props }) => {
  const childrenWithProps = React.Children.map(children, child => {
    if (!React.isValidElement(child)) return child;
    
    return React.cloneElement(child, {
      activeTab,
      setActiveTab
    });
  });

  return (
    <div
      className={cn(
        "inline-flex h-12 items-center justify-center rounded-xl bg-glass-light dark:bg-glass-dark-light p-1 text-gray-700 dark:text-gray-300",
        className
      )}
      {...props}
    >
      {childrenWithProps}
    </div>
  );
};

export const TabsTrigger = ({ children, value, activeTab, setActiveTab, className, ...props }) => {
  const isActive = activeTab === value;
  
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-lg px-6 py-2 text-sm font-medium ring-offset-white transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 relative",
        isActive
          ? "bg-gradient-to-r from-primary to-secondary text-white shadow-lg font-semibold"
          : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700",
        className
      )}
      onClick={() => setActiveTab && setActiveTab(value)}
      {...props}
    >
      {isActive && (
        <motion.div
          className="absolute inset-0 rounded-lg bg-gradient-to-r from-primary to-secondary shadow-lg"
          layoutId="activeTab"
          transition={{ type: "spring", stiffness: 400, damping: 30 }}
        />
      )}
      <span className="relative z-10">{children}</span>
    </button>
  );
};

export const TabsContent = ({ children, value, activeTab, className, ...props }) => {
  if (activeTab !== value) return null;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className={cn("mt-6", className)}
      {...props}
    >
      {children}
    </motion.div>
  );
};