import React from "react";
import { motion } from "framer-motion";
import { 
  RefreshCw,
  ChevronRight,
  Zap,
  AlertCircle
} from "lucide-react";
import { Button } from "./button";

const GenerateButton = ({ 
  onGenerate, 
  onReset, 
  isLoading, 
  isReset, 
  canGenerate 
}) => {
  const getButtonContent = () => {
    if (isLoading) {
      return (
        <>
          <RefreshCw className="mr-2 h-5 w-5 animate-spin" />
          Generating...
        </>
      );
    }
    
    if (isReset) {
      return (
        <>
          <RefreshCw className="mr-2 h-5 w-5" />
          Start Over
        </>
      );
    }
    
    if (!canGenerate) {
      return (
        <>
          <AlertCircle className="mr-2 h-5 w-5" />
          Select Profile & Distribution
        </>
      );
    }
    
    return (
      <>
        <Zap className="mr-2 h-5 w-5" />
        Generate FOCUS CUR
        <ChevronRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
      </>
    );
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.8 }}
      className="text-center mb-8"
    >
      <Button
        onClick={isReset ? onReset : onGenerate}
        disabled={!canGenerate || isLoading}
        variant={isReset ? "secondary" : canGenerate ? "default" : "ghost"}
        size="lg"
        className={`min-w-[240px] group transition-all duration-300 ${
          !canGenerate && !isReset 
            ? 'opacity-50 cursor-not-allowed' 
            : 'hover:shadow-glow'
        }`}
      >
        {getButtonContent()}
      </Button>
      
      {!canGenerate && !isReset && (
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-sm text-gray-500 mt-3"
        >
          Please complete your selections above to continue
        </motion.p>
      )}
    </motion.div>
  );
};

export default GenerateButton;