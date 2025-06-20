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
import GenerateButton from "./components/ui/GenerateButton";
import ResultCard from "./components/ui/ResultCard";
import Footer from "./components/sections/Footer";
import { Toaster } from "./components/ui/toaster";
import DarkModeToggle from "./components/ui/DarkModeToggle";
import { LoadingSkeleton } from "./components/ui/LoadingSkeleton";

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

  const canGenerate = selectedProfile && distribution;

  // Show content after theme is loaded to prevent flash
  React.useEffect(() => {
    if (isLoaded) {
      const timer = setTimeout(() => setShowContent(true), 100);
      return () => clearTimeout(timer);
    }
  }, [isLoaded]);

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

            {/* Generate Button */}
            <FloatingElement delay={0.8}>
              <GenerateButton 
                onGenerate={generateCUR}
                onReset={resetSelections}
                isLoading={isLoading}
                isReset={isReset}
                canGenerate={canGenerate}
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
            />
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