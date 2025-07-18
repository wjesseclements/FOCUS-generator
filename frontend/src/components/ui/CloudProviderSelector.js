import React from "react";
import { motion } from "framer-motion";
import { Cloud, Check } from "lucide-react";
import { cn } from "../../lib/utils.js";
import Tooltip from "./Tooltip";

const providers = [
  {
    id: "aws",
    name: "AWS",
    fullName: "Amazon Web Services",
    color: "from-orange-500 to-orange-600",
    bgColor: "bg-orange-100 dark:bg-orange-900/30",
    borderColor: "border-orange-500",
    description: "EC2, S3, RDS, Lambda, and more"
  },
  {
    id: "azure",
    name: "Azure",
    fullName: "Microsoft Azure",
    color: "from-blue-500 to-blue-600",
    bgColor: "bg-blue-100 dark:bg-blue-900/30",
    borderColor: "border-blue-500",
    description: "VMs, Blob Storage, SQL Database, Functions"
  },
  {
    id: "gcp",
    name: "GCP",
    fullName: "Google Cloud Platform",
    color: "from-green-500 to-green-600",
    bgColor: "bg-green-100 dark:bg-green-900/30",
    borderColor: "border-green-500",
    description: "Compute Engine, Cloud Storage, BigQuery"
  }
];

const CloudProviderSelector = ({ selectedProviders, onProviderToggle }) => {
  const handleToggle = (providerId) => {
    if (selectedProviders.includes(providerId)) {
      onProviderToggle(selectedProviders.filter(id => id !== providerId));
    } else {
      onProviderToggle([...selectedProviders, providerId]);
    }
  };

  return (
    <div className="w-full mb-8">
      <div className="flex items-center justify-center mb-4">
        <Cloud className="h-5 w-5 text-primary mr-2" />
        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100">
          Select Cloud Providers
        </h3>
      </div>
      <p className="text-center text-sm text-gray-600 dark:text-gray-400 mb-6">
        Choose one or more providers to include in your FOCUS dataset
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl mx-auto">
        {providers.map((provider) => {
          const isSelected = selectedProviders.includes(provider.id);
          
          return (
            <motion.div
              key={provider.id}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              transition={{ duration: 0.1 }}
            >
              <Tooltip content={provider.description} placement="top">
                <div
                  onClick={() => handleToggle(provider.id)}
                  className={cn(
                    "relative cursor-pointer rounded-xl p-4 transition-all duration-300",
                    "bg-glass-light dark:bg-glass-dark-light",
                    "border-2",
                    isSelected 
                      ? `${provider.borderColor} ${provider.bgColor}` 
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                  )}
                >
                  {isSelected && (
                    <motion.div
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ type: "spring", stiffness: 200, damping: 20 }}
                      className="absolute -top-2 -right-2 z-10"
                    >
                      <div className={cn("rounded-full p-1 bg-gradient-to-br", provider.color)}>
                        <Check className="h-4 w-4 text-white" />
                      </div>
                    </motion.div>
                  )}
                  
                  <div className="flex flex-col items-center text-center">
                    <div className={cn(
                      "w-12 h-12 rounded-lg mb-3 flex items-center justify-center",
                      "bg-gradient-to-br text-white shadow-lg",
                      provider.color
                    )}>
                      <Cloud size={24} />
                    </div>
                    <h4 className="font-semibold text-gray-800 dark:text-gray-100">
                      {provider.name}
                    </h4>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      {provider.fullName}
                    </p>
                  </div>
                </div>
              </Tooltip>
            </motion.div>
          );
        })}
      </div>
      
      {selectedProviders.length === 0 && (
        <p className="text-center text-sm text-red-500 dark:text-red-400 mt-4">
          Please select at least one cloud provider
        </p>
      )}
    </div>
  );
};

export default CloudProviderSelector;