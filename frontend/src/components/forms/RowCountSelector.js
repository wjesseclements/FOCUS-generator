import React from "react";
import { motion } from "framer-motion";
import { BarChart3, Info } from "lucide-react";
import { Card, CardContent } from "../ui/card";
import Tooltip from "../ui/Tooltip";

const RowCountSelector = ({ rowCount, onRowCountChange, onInputChange }) => {
  const getRowCountCategory = (count) => {
    if (count <= 20) return { label: "Quick Test", color: "text-green-600 dark:text-green-400", bg: "bg-green-100 dark:bg-green-900/30" };
    if (count <= 50) return { label: "Small Dataset", color: "text-blue-600 dark:text-blue-400", bg: "bg-blue-100 dark:bg-blue-900/30" };
    if (count <= 100) return { label: "Medium Dataset", color: "text-yellow-600 dark:text-yellow-400", bg: "bg-yellow-100 dark:bg-yellow-900/30" };
    if (count <= 500) return { label: "Large Dataset", color: "text-orange-600 dark:text-orange-400", bg: "bg-orange-100 dark:bg-orange-900/30" };
    return { label: "Extra Large", color: "text-red-600 dark:text-red-400", bg: "bg-red-100 dark:bg-red-900/30" };
  };

  const category = getRowCountCategory(parseInt(rowCount));

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6 }}
      className="mb-8"
    >
      <motion.div
        whileHover={{ 
          scale: 1.005,
          y: -2,
          transition: { duration: 0.15, ease: "easeOut" }
        }}
      >
        <Card className="max-w-lg mx-auto">
          <CardContent className="p-8">
            <div className="text-center mb-6">
              <div className="flex items-center justify-center mb-3">
                <BarChart3 className="h-6 w-6 text-primary mr-2" />
                <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">
                  Dataset Size
                </h2>
                <Tooltip 
                  content="Higher values generate more comprehensive data but may take longer to process"
                  placement="top"
                >
                  <Info className="h-4 w-4 text-gray-400 dark:text-gray-500 ml-2 cursor-help" />
                </Tooltip>
              </div>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                Configure the number of rows in your FOCUS report
              </p>
            </div>
          
          {/* Category Badge */}
          <div className="flex justify-center mb-6">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${category.bg} ${category.color}`}>
              {category.label}
            </span>
          </div>
          
          {/* Row Count Display */}
          <div className="text-center mb-6">
            <div className="text-4xl font-bold text-gray-800 dark:text-gray-100 mb-2">
              {rowCount}
            </div>
            <div className="text-gray-500 dark:text-gray-400 text-sm">rows</div>
          </div>
          
          {/* Range Slider */}
          <div className="mb-6">
            <input
              type="range"
              min="1"
              max="100"
              value={rowCount}
              onChange={(e) => onRowCountChange(e.target.value)}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              style={{
                background: `linear-gradient(to right, #667eea 0%, #667eea ${(rowCount / 100) * 100}%, #e5e7eb ${(rowCount / 100) * 100}%, #e5e7eb 100%)`
              }}
            />
            <div className="flex justify-between text-xs text-gray-500 mt-2">
              <span>1</span>
              <span>25</span>
              <span>50</span>
              <span>75</span>
              <span>100</span>
            </div>
          </div>
          
          {/* Manual Input */}
          <div className="flex justify-center items-center space-x-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Exact value:
            </label>
            <input
              type="number"
              min="1"
              max="1000"
              value={rowCount}
              onChange={onInputChange}
              className="w-20 px-3 py-2 rounded-xl input-glass text-center font-semibold focus:ring-2 focus:ring-primary/50 transition-all"
            />
          </div>
          
          {/* Recommendations */}
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">💡 Recommendations:</h4>
            <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              <li>• <strong>1-20 rows:</strong> Quick testing and validation</li>
              <li>• <strong>20-100 rows:</strong> Dashboard development</li>
              <li>• <strong>100-500 rows:</strong> Comprehensive analysis</li>
            </ul>
          </div>
        </CardContent>
      </Card>
      </motion.div>
    </motion.div>
  );
};

export default RowCountSelector;