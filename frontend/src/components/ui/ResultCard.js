import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Sparkles,
  Download,
  FileSpreadsheet,
  Clock,
  CheckCircle2,
  BarChart2,
  Eye,
  EyeOff
} from "lucide-react";
import { Button } from "./button";
import { Card, CardContent } from "./card";

const ResultCard = ({ response, rowCount, onDownload, showVisualization, onToggleVisualization }) => {
  // Debug logging
  if (response) {
    console.log('ResultCard response:', response);
    console.log('Download URL:', response.downloadUrl);
  }
  
  return (
    <AnimatePresence>
      {response && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.9 }}
          transition={{ type: "spring", stiffness: 200, damping: 20 }}
          className="max-w-md mx-auto"
        >
          <Card className="bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 border-green-200 shadow-xl">
            <CardContent className="p-8 text-center">
              {/* Success Icon with Animation */}
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ type: "spring", stiffness: 200, damping: 15, delay: 0.2 }}
                className="w-20 h-20 bg-gradient-to-br from-green-400 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg"
              >
                <Sparkles className="h-10 w-10 text-white" />
              </motion.div>
              
              {/* Success Message */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <h3 className="font-bold text-2xl text-green-800 mb-2 flex items-center justify-center">
                  <CheckCircle2 className="h-6 w-6 mr-2" />
                  Generation Complete!
                </h3>
                <p className="text-green-700 mb-6 leading-relaxed">
                  {response.message}
                </p>
              </motion.div>
              
              {/* File Details */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="bg-white/70 backdrop-blur-sm rounded-xl p-4 mb-6 border border-green-200"
              >
                <div className="flex items-center justify-center text-gray-700 mb-2">
                  <FileSpreadsheet className="h-5 w-5 mr-2" />
                  <span className="font-semibold">FOCUS CUR Report</span>
                </div>
                <div className="flex items-center justify-center text-sm text-gray-600">
                  <Clock className="h-4 w-4 mr-1" />
                  <span>{rowCount} rows • CSV format</span>
                </div>
              </motion.div>
              
              {/* Download Button */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.8, type: "spring", stiffness: 200 }}
              >
                <a
                  href={response.downloadUrl}
                  download
                  onClick={(e) => {
                    console.log('Download clicked, URL:', response.downloadUrl);
                    if (onDownload) onDownload(e);
                  }}
                  className="inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-medium transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-11 px-8 bg-glass-light dark:bg-glass-dark-light backdrop-blur-md border border-white/20 dark:border-white/10 text-gray-700 dark:text-gray-200 shadow-glass hover:bg-glass-light/80 dark:hover:bg-glass-dark-light/80 hover:shadow-glass-inset group w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:from-green-600 hover:to-emerald-700 shadow-lg hover:shadow-xl"
                >
                  <Download className="mr-2 h-5 w-5 group-hover:animate-bounce" />
                  Download Your Report
                </a>
              </motion.div>

              {/* Visualization Toggle Button */}
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.9, type: "spring", stiffness: 200 }}
                className="mt-4"
              >
                <Button
                  onClick={onToggleVisualization}
                  variant="outline"
                  className="w-full bg-white/80 hover:bg-white/90 dark:bg-gray-800/80 dark:hover:bg-gray-800/90 border-blue-200 dark:border-blue-700 text-blue-700 dark:text-blue-300"
                >
                  {showVisualization ? (
                    <>
                      <EyeOff className="mr-2 h-5 w-5" />
                      Hide Visualization
                    </>
                  ) : (
                    <>
                      <BarChart2 className="mr-2 h-5 w-5" />
                      Visualize Data
                    </>
                  )}
                </Button>
              </motion.div>
              
              {/* Additional Info */}
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1 }}
                className="text-xs text-gray-500 mt-4"
              >
                Your file will download automatically. It's ready for analysis!
              </motion.p>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default ResultCard;