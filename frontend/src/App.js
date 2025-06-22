import React from "react";
import { toast } from "sonner";
import { AnimatePresence } from "framer-motion";

// Context
import { ThemeProvider, useTheme } from "./contexts/ThemeContext";

// Components
import HeroSection from "./components/sections/HeroSection";
import ProfileSelection from "./components/sections/ProfileSelection";
import DistributionSelection from "./components/sections/DistributionSelection";
import RowCountSelector from "./components/forms/RowCountSelector";
import CloudProviderSelector from "./components/ui/CloudProviderSelector";
import TrendOptions from "./components/ui/TrendOptions";
import GenerateButton from "./components/ui/GenerateButton";
import ResultCard from "./components/ui/ResultCard";
import Footer from "./components/sections/Footer";
import { Toaster } from "./components/ui/toaster";
import DarkModeToggle from "./components/ui/DarkModeToggle";
import { LoadingSkeleton } from "./components/ui/LoadingSkeleton";
import CURVisualization from "./components/sections/CURVisualization";

// Animations
import { 
  AppEntrance, 
  PageTransition, 
  StaggeredContainer, 
  FloatingElement 
} from "./components/animations/PageTransition";
import { MagneticCard } from "./components/ui/MicroInteractions";

// Hooks
import { useFocusGenerator } from "./hooks/useFocusGenerator";

function AppContent() {
  const { isLoaded } = useTheme();
  const [showContent, setShowContent] = React.useState(false);
  const [selectedProviders, setSelectedProviders] = React.useState(['aws']);
  const [multiMonth, setMultiMonth] = React.useState(false);
  const [trendOptions, setTrendOptions] = React.useState({
    monthCount: 6,
    scenario: "linear",
    parameters: {}
  });
  const [showVisualization, setShowVisualization] = React.useState(false);
  const [csvData, setCsvData] = React.useState(null);
  
  const {
    selectedProfile,
    setSelectedProfile,
    distribution,
    setDistribution,
    rowCount,
    handleRowCountChange,
    response,
    isReset,
    isLoading,
    generateCUR,
    resetSelections
  } = useFocusGenerator();

  // Show content after theme is loaded to prevent flash
  React.useEffect(() => {
    if (isLoaded) {
      const timer = setTimeout(() => setShowContent(true), 100);
      return () => clearTimeout(timer);
    }
  }, [isLoaded]);

  // Parse CSV data from response
  const parseCSVData = React.useCallback((csvText) => {
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    
    const data = [];
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',');
      const row = {};
      headers.forEach((header, index) => {
        row[header] = values[index]?.trim() || '';
      });
      data.push(row);
    }
    return data;
  }, []);

  // Fetch and parse CSV when response is available
  React.useEffect(() => {
    if (response && response.downloadUrl) {
      // Reset visualization state when new data is generated
      setShowVisualization(false);
      
      // Fetch the CSV data
      fetch(response.downloadUrl)
        .then(res => res.text())
        .then(csvText => {
          const parsedData = parseCSVData(csvText);
          setCsvData(parsedData);
        })
        .catch(err => {
          console.error("Error fetching CSV data:", err);
          toast.error("Could not load data for visualization");
        });
    }
  }, [response, parseCSVData]);

  const handleDownload = () => {
    toast.success("Download started!", {
      description: "Your FOCUS CUR file is being downloaded."
    });
  };

  if (!showContent) {
    return <LoadingSkeleton variant="cards" />;
  }

  return (
    <AppEntrance>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-dark-bg dark:to-dark-surface overflow-hidden transition-colors duration-500">
        {/* Dark mode toggle */}
        <DarkModeToggle className="fixed top-6 right-6 z-50" />
        
        {/* Animated background elements */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-radial opacity-30 dark:opacity-20 blur-3xl animate-pulse-slow" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-radial opacity-20 dark:opacity-10 blur-3xl animate-pulse-slow" style={{ animationDelay: '2s' }} />
        </div>

        {/* Main content */}
        <PageTransition className="relative z-10 min-h-screen flex flex-col items-center pb-24">
          {/* Hero Section */}
          <FloatingElement>
            <HeroSection />
          </FloatingElement>

          {/* Main Content Container */}
          <StaggeredContainer className="w-full max-w-6xl px-4 mt-8 space-y-8">
            {/* Cloud Provider Selection */}
            <MagneticCard>
              <CloudProviderSelector
                selectedProviders={selectedProviders}
                onProviderToggle={setSelectedProviders}
              />
            </MagneticCard>

            {/* Profile Selection */}
            <MagneticCard>
              <ProfileSelection 
                selectedProfile={selectedProfile}
                onProfileSelect={setSelectedProfile}
              />
            </MagneticCard>

            {/* Distribution Selection */}
            <MagneticCard>
              <DistributionSelection 
                selectedDistribution={distribution}
                onDistributionSelect={setDistribution}
              />
            </MagneticCard>

            {/* Row Count Selector */}
            <FloatingElement delay={0.6}>
              <RowCountSelector 
                rowCount={rowCount}
                onRowCountChange={handleRowCountChange}
                onInputChange={(e) => handleRowCountChange(e.target.value)}
              />
            </FloatingElement>

            {/* Multi-Month Toggle */}
            <FloatingElement delay={0.7}>
              <div className="max-w-lg mx-auto">
                <label className="flex items-center justify-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={multiMonth}
                    onChange={(e) => setMultiMonth(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/25 dark:peer-focus:ring-primary/50 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                  <span className="ml-3 text-sm font-medium text-gray-900 dark:text-gray-300">
                    Generate Multiple Months
                  </span>
                </label>
              </div>
            </FloatingElement>

            {/* Trend Options - Show when multiMonth is enabled */}
            <AnimatePresence>
              {multiMonth && (
                <FloatingElement delay={0.75}>
                  <TrendOptions onOptionsChange={setTrendOptions} />
                </FloatingElement>
              )}
            </AnimatePresence>

            {/* Generate Button */}
            <FloatingElement delay={0.8}>
              <GenerateButton 
                onGenerate={() => generateCUR(selectedProviders, trendOptions, multiMonth)}
                onReset={resetSelections}
                isLoading={isLoading}
                isReset={isReset}
                canGenerate={selectedProfile && distribution && selectedProviders.length > 0}
                multiMonth={multiMonth}
              />
            </FloatingElement>

            {/* Loading State */}
            <AnimatePresence>
              {isLoading && (
                <LoadingSkeleton variant="generating" />
              )}
            </AnimatePresence>

            {/* Success Response */}
            <ResultCard 
              response={response}
              rowCount={rowCount}
              onDownload={handleDownload}
              showVisualization={showVisualization}
              onToggleVisualization={() => setShowVisualization(!showVisualization)}
            />

            {/* CUR Visualization */}
            <AnimatePresence>
              {showVisualization && csvData && (
                <FloatingElement delay={0.2}>
                  <CURVisualization data={csvData} />
                </FloatingElement>
              )}
            </AnimatePresence>
          </StaggeredContainer>
        </PageTransition>

        {/* Footer */}
        <Footer />
        
        {/* Toast Notifications */}
        <Toaster 
          position="top-right"
          expand={true}
          richColors={true}
        />
      </div>
    </AppEntrance>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}