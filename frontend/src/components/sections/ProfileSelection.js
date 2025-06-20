import React from "react";
import { motion } from "framer-motion";
import { 
  Database, 
  Cpu, 
  Sparkles
} from "lucide-react";
import ProfileCard from "../ui/ProfileCard";

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

const profiles = [
  {
    name: "Greenfield",
    description: "For startups or small businesses ($20k–$50k/month).",
    icon: Sparkles,
    gradient: "from-green-400 to-blue-500",
  },
  {
    name: "Large Business",
    description: "For medium-sized organizations ($100k–$250k/month).",
    icon: Database,
    gradient: "from-blue-500 to-purple-600",
  },
  {
    name: "Enterprise",
    description: "For large corporations ($1M+/month).",
    icon: Cpu,
    gradient: "from-purple-600 to-pink-600",
  },
];

const ProfileSelection = ({ selectedProfile, onProfileSelect }) => {
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
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Choose Your Profile
        </h2>
        <p className="text-gray-600">
          Select the profile that best matches your organization size
        </p>
      </motion.div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {profiles.map((profile) => (
          <ProfileCard
            key={profile.name}
            profile={profile}
            isSelected={selectedProfile === profile.name}
            onSelect={onProfileSelect}
          />
        ))}
      </div>
    </motion.div>
  );
};

export default ProfileSelection;