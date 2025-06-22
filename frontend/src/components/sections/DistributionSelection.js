import React from "react";
import { motion } from "framer-motion";
import { 
  Database, 
  Cpu, 
  HardDrive, 
  Film
} from "lucide-react";
import DistributionCard from "../ui/DistributionCard";

const staggerChildren = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};

const distributions = [
  { 
    name: "Evenly Distributed", 
    description: "Evenly spread across services.",
    icon: Database,
    gradient: "from-cyan-400 to-blue-600"
  },
  { 
    name: "ML-Focused", 
    description: "Emphasizing SageMaker and ML workloads.",
    icon: Cpu,
    gradient: "from-purple-500 to-pink-600"
  },
  { 
    name: "Data-Intensive", 
    description: "Focus on S3, Redshift, and data-heavy services.",
    icon: HardDrive,
    gradient: "from-orange-400 to-red-600"
  },
  { 
    name: "Media-Intensive", 
    description: "Optimized for high storage and bandwidth needs.",
    icon: Film,
    gradient: "from-pink-500 to-rose-600"
  },
];

const DistributionSelection = ({ selectedDistribution, onDistributionSelect }) => {
  return (
    <motion.div 
      variants={staggerChildren}
      initial="initial"
      animate="animate"
      className="mb-8"
    >
      <motion.div 
        variants={fadeInUp} 
        className="text-center mb-6"
      >
        <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-2">
          Select Distribution
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Choose how you want the cost data to be distributed across services
        </p>
      </motion.div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {distributions.map((dist) => (
          <DistributionCard
            key={dist.name}
            distribution={dist}
            isSelected={selectedDistribution === dist.name}
            onSelect={onDistributionSelect}
            compact={true}
          />
        ))}
      </div>
    </motion.div>
  );
};

export default DistributionSelection;