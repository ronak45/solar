import React from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '../layout/Layout';
import { Camera, BookOpen, Clock, Sparkles } from 'lucide-react';

export function HomePage() {
  return (
    <Layout>
      <div className="space-y-12">
        {/* Hero Section */}
        <div className="text-center space-y-6">
          <h1 className="text-5xl font-bold text-gray-900">
            Welcome to <span className="text-orange-600">CookQuest</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Turn pantry chaos into culinary adventures. Scan your ingredients, 
            discover interactive recipes, and make every cooking session a choose-your-own-dish experience.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon={<Camera className="h-8 w-8" />}
            title="Smart Pantry Scanning"
            description="Point your camera at your pantry and instantly inventory what you own. No manual typing required."
            link="/pantry"
            linkText="Scan Pantry"
            color="bg-blue-50 text-blue-600"
          />
          
          <FeatureCard
            icon={<BookOpen className="h-8 w-8" />}
            title="Interactive Recipes"
            description="Discover recipes with branching choices that let you steer the plot. Every dish becomes a unique adventure."
            link="/recipes"
            linkText="Browse Recipes"
            color="bg-green-50 text-green-600"
          />
          
          <FeatureCard
            icon={<Clock className="h-8 w-8" />}
            title="Cooking Sessions"
            description="Track your culinary journeys and replay your favorite paths. Build a collection of cooking stories."
            link="/sessions"
            linkText="View Sessions"
            color="bg-purple-50 text-purple-600"
          />
        </div>

        {/* Getting Started */}
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-orange-100">
          <div className="text-center space-y-6">
            <div className="flex justify-center">
              <Sparkles className="h-12 w-12 text-orange-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900">Ready to Start Your Quest?</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Begin by scanning your pantry to see what ingredients you have available. 
              Then explore recipes tailored to your inventory and start cooking!
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/pantry"
                className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 transition-colors"
              >
                <Camera className="h-5 w-5 mr-2" />
                Scan My Pantry
              </Link>
              <Link
                to="/recipes"
                className="inline-flex items-center justify-center px-6 py-3 border border-orange-300 text-base font-medium rounded-md text-orange-600 bg-white hover:bg-orange-50 transition-colors"
              >
                <BookOpen className="h-5 w-5 mr-2" />
                Explore Recipes
              </Link>
            </div>
          </div>
        </div>

        {/* How It Works */}
        <div className="space-y-8">
          <h2 className="text-3xl font-bold text-center text-gray-900">How CookQuest Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <StepCard
              number="1"
              title="Scan & Inventory"
              description="Use your camera to scan pantry items or manually add ingredients you have available."
            />
            <StepCard
              number="2"
              title="Choose Your Adventure"
              description="Select a recipe and make branching decisions that affect ingredients, techniques, and flavors."
            />
            <StepCard
              number="3"
              title="Cook & Document"
              description="Follow interactive guidance, take photos, and create your unique culinary story."
            />
          </div>
        </div>
      </div>
    </Layout>
  );
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  link: string;
  linkText: string;
  color: string;
}

function FeatureCard({ icon, title, description, link, linkText, color }: FeatureCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow border border-gray-100">
      <div className={`inline-flex p-3 rounded-lg ${color} mb-4`}>
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-gray-900 mb-3">{title}</h3>
      <p className="text-gray-600 mb-4">{description}</p>
      <Link
        to={link}
        className="inline-flex items-center text-orange-600 hover:text-orange-700 font-medium"
      >
        {linkText} →
      </Link>
    </div>
  );
}

interface StepCardProps {
  number: string;
  title: string;
  description: string;
}

function StepCard({ number, title, description }: StepCardProps) {
  return (
    <div className="text-center">
      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-orange-600 text-white font-bold text-lg mb-4">
        {number}
      </div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}