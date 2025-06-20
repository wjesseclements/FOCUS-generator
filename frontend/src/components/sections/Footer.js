import React from "react";
import { motion } from "framer-motion";
import { Shield, AlertTriangle } from "lucide-react";

const Footer = () => {
  return (
    <motion.footer 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1 }}
      className="fixed bottom-0 w-full z-20"
    >
      <div className="glass border-t border-white/10 py-4 px-4 text-center backdrop-blur-xl">
        <div className="flex items-center justify-center text-sm text-gray-700">
          <AlertTriangle className="h-4 w-4 mr-2 text-amber-600" />
          <span className="font-medium">Disclaimer:</span>
          <span className="ml-1">
            This data is synthetic and for testing purposes only. 
            Not affiliated with AWS or FinOps Foundation.
          </span>
          <Shield className="h-4 w-4 ml-2 text-green-600" />
        </div>
      </div>
    </motion.footer>
  );
};

export default Footer;