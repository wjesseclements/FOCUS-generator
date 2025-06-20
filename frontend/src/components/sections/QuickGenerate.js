import React from "react";
import { motion } from "framer-motion";
import CloudProviderSelector from "../ui/CloudProviderSelector";
import RowCountSelector from "../forms/RowCountSelector";
import ProfileSelection from "./ProfileSelection";
import DistributionSelection from "./DistributionSelection";
import GenerateButton from "../ui/GenerateButton";
import ResultCard from "../ui/ResultCard";
import { LoadingSkeleton } from "../ui/LoadingSkeleton";

const QuickGenerate = ({ 
  selectedProviders,
  onProviderToggle,
  rowCount,
  onRowCountChange,
  onRowCountInputChange,
  selectedProfile,
  onProfileSelect,
  selectedDistribution,
  onDistributionSelect,
  onGenerate,
  isLoading,
  downloadUrl,
  fileSize,
  generationTime,
  onReset
}) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <CloudProviderSelector
        selectedProviders={selectedProviders}
        onProviderToggle={onProviderToggle}
      />
      
      <RowCountSelector
        rowCount={rowCount}
        onRowCountChange={onRowCountChange}
        onInputChange={onRowCountInputChange}
      />
      
      <ProfileSelection
        selectedProfile={selectedProfile}
        onProfileSelect={onProfileSelect}
      />
      
      <DistributionSelection
        selectedDistribution={selectedDistribution}
        onDistributionSelect={onDistributionSelect}
      />
      
      <GenerateButton
        onClick={() => onGenerate(selectedProviders)}
        isLoading={isLoading}
        disabled={selectedProviders.length === 0 || !selectedProfile || !selectedDistribution}
      />
      
      {isLoading && <LoadingSkeleton />}
      
      {downloadUrl && !isLoading && (
        <ResultCard
          downloadUrl={downloadUrl}
          fileSize={fileSize}
          generationTime={generationTime}
          onReset={onReset}
        />
      )}
    </motion.div>
  );
};

export default QuickGenerate;