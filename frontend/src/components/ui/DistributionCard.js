import React from "react";
import { motion } from "framer-motion";
import { CheckCircle2 } from "lucide-react";
import Tooltip from "./Tooltip";
import { Card, CardContent } from "./card";

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

const DistributionCard = React.memo(({ 
  distribution, 
  isSelected, 
  onSelect,
  compact = false
}) => {
  const Icon = distribution.icon;
  
  return (
    <motion.div variants={fadeInUp}>
      <Tooltip 
        content={distribution.description} 
        placement="top"
      >
        <Card
          onClick={() => onSelect(distribution.name)}
          className={`cursor-pointer transition-all duration-300 hover:scale-105 relative ${
            isSelected
              ? 'ring-2 ring-primary ring-offset-2 shadow-xl'
              : 'hover:shadow-lg'
          }`}
        >
          {isSelected && (
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ type: "spring", stiffness: 200, damping: 20 }}
              className="absolute -top-2 -right-2 z-10"
            >
              <div className="bg-green-500 rounded-full p-1">
                <CheckCircle2 className="h-4 w-4 text-white" />
              </div>
            </motion.div>
          )}
          <CardContent className={compact ? "p-4 text-center" : "p-6"}>
            {compact ? (
              <>
                <div className={`p-3 rounded-xl bg-gradient-to-br ${distribution.gradient} text-white mx-auto w-fit mb-3 shadow-lg`}>
                  <Icon size={20} />
                </div>
                <h3 className="font-medium text-gray-800 dark:text-gray-100">{distribution.name}</h3>
              </>
            ) : (
              <div className="flex items-center space-x-4">
                <div className={`p-3 rounded-xl bg-gradient-to-br ${distribution.gradient} text-white shadow-lg`}>
                  <Icon size={24} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg text-gray-800 dark:text-gray-100">{distribution.name}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{distribution.description}</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </Tooltip>
    </motion.div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison for better performance
  return prevProps.isSelected === nextProps.isSelected &&
         prevProps.distribution.name === nextProps.distribution.name &&
         prevProps.compact === nextProps.compact;
});

export default DistributionCard;