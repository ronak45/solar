import { Clock, Camera, Mic, ArrowLeft, ArrowRight, Star, CircleCheck } from "lucide-react";
import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout } from '../layout/Layout';

import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Textarea } from '../ui/textarea';
import { 
  cookingServiceGetCookingSession, 
  cookingServiceMakeCookingDecision, 
  cookingServiceUpdateCurrentStep,
  cookingServiceAddCookingPhoto,
  cookingServiceProcessVoiceQuestion,
  cookingServiceCompleteCookingSession
} from '../../lib/sdk';
import type { CookingSession } from '../../lib/sdk';

export function CookingPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [session, setSession] = useState<CookingSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [voiceQuestion, setVoiceQuestion] = useState('');
  const [showVoiceInput, setShowVoiceInput] = useState(false);
  const [showRating, setShowRating] = useState(false);
  const [rating, setRating] = useState(0);
  const [notes, setNotes] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (sessionId) {
      loadCookingSession();
    }
  }, [sessionId]);

  const loadCookingSession = async () => {
    if (!sessionId) return;
    
    try {
      setIsLoading(true);
      const response = await cookingServiceGetCookingSession({
        body: { session_id: sessionId }
      });
      if (response.data) {
        setSession(response.data);
      }
    } catch (error) {
      console.error('Failed to load cooking session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMakeDecision = async (branchPoint: number, choice: string) => {
    if (!sessionId) return;

    try {
      const response = await cookingServiceMakeCookingDecision({
        body: {
          session_id: sessionId,
          branch_point: branchPoint,
          choice: choice
        }
      });
      
      if (response.data) {
        loadCookingSession(); // Refresh session data
      }
    } catch (error) {
      console.error('Failed to make cooking decision:', error);
    }
  };

  const handleNextStep = async () => {
    if (!sessionId || !session) return;

    try {
      await cookingServiceUpdateCurrentStep({
        body: {
          session_id: sessionId,
          step_number: session.current_step + 1
        }
      });
      loadCookingSession();
    } catch (error) {
      console.error('Failed to update step:', error);
    }
  };

  const handlePreviousStep = async () => {
    if (!sessionId || !session || session.current_step <= 1) return;

    try {
      await cookingServiceUpdateCurrentStep({
        body: {
          session_id: sessionId,
          step_number: session.current_step - 1
        }
      });
      loadCookingSession();
    } catch (error) {
      console.error('Failed to update step:', error);
    }
  };

  const handleAddPhoto = async (file: File) => {
    if (!sessionId || !session) return;

    try {
      const response = await cookingServiceAddCookingPhoto({
        body: {
          photo: file,
          session_id: sessionId,
          step_number: session.current_step
        }
      });
      
      if (response.data) {
        loadCookingSession();
      }
    } catch (error) {
      console.error('Failed to add photo:', error);
    }
  };

  const handleVoiceQuestion = async () => {
    if (!sessionId || !voiceQuestion.trim()) return;

    try {
      const response = await cookingServiceProcessVoiceQuestion({
        body: {
          session_id: sessionId,
          question: voiceQuestion
        }
      });
      
      if (response.data) {
        console.log('Voice response:', response.data);
        setVoiceQuestion('');
        setShowVoiceInput(false);
        loadCookingSession();
      }
    } catch (error) {
      console.error('Failed to process voice question:', error);
    }
  };

  const handleCompleteSession = async () => {
    if (!sessionId) return;

    try {
      const response = await cookingServiceCompleteCookingSession({
        body: {
          session_id: sessionId,
          rating: rating || undefined,
          notes: notes || undefined,
          would_make_again: rating >= 4
        }
      });
      
      if (response.data) {
        navigate('/sessions');
      }
    } catch (error) {
      console.error('Failed to complete session:', error);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleAddPhoto(file);
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
          <p className="text-gray-600 mt-2">Loading cooking session...</p>
        </div>
      </Layout>
    );
  }

  if (!session) {
    return (
      <Layout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Session not found</h2>
          <Button onClick={() => navigate('/recipes')}>
            Back to Recipes
          </Button>
        </div>
      </Layout>
    );
  }

  const currentStep = session.final_steps.find(step => step.step === session.current_step);
  const totalSteps = session.final_steps.length;
  const progress = (session.current_step / totalSteps) * 100;

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={() => navigate('/recipes')}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Recipes
          </Button>
          
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900">Cooking Quest</h1>
            <p className="text-gray-600">Step {session.current_step} of {totalSteps}</p>
          </div>
          
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
            >
              <Camera className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowVoiceInput(true)}
            >
              <Mic className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Progress */}
        <div className="space-y-2">
          <Progress value={progress} className="w-full" />
          <p className="text-sm text-gray-600 text-center">
            {Math.round(progress)}% complete
          </p>
        </div>

        {/* Current Step */}
        {currentStep && (
          <Card className="border-orange-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="bg-orange-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold">
                  {session.current_step}
                </span>
                Current Step
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-lg mb-4">{currentStep.instruction}</p>
              
              {currentStep.time_minutes > 0 && (
                <div className="flex items-center gap-2 text-orange-600 mb-4">
                  <Clock className="h-4 w-4" />
                  <span>{currentStep.time_minutes} minutes</span>
                </div>
              )}

              {/* Decision Points */}
              {/* This would be populated based on branch_points in the recipe */}
              
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={handlePreviousStep}
                  disabled={session.current_step <= 1}
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Previous
                </Button>
                
                {session.current_step >= totalSteps ? (
                  <Button
                    onClick={() => setShowRating(true)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <CircleCheck className="h-4 w-4 mr-2" />
                    Complete Quest
                  </Button>
                ) : (
                  <Button
                    onClick={handleNextStep}
                    className="bg-orange-600 hover:bg-orange-700"
                  >
                    Next Step
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Nutrition Info */}
        <div className="grid md:grid-cols-2 gap-6">
          <NutritionCard nutrition={session.final_nutrition} />
          <IngredientsList ingredients={session.final_ingredients} />
        </div>

        {/* Session Photos */}
        {session.session_photos.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Quest Photos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {session.session_photos.map((photo, index) => (
                  <img
                    key={index}
                    src={photo}
                    alt={`Cooking step ${index + 1}`}
                    className="w-full h-24 object-cover rounded-md"
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Voice Input Modal */}
        {showVoiceInput && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Ask a Cooking Question</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Can I substitute this ingredient? How do I know when it's done?"
                  value={voiceQuestion}
                  onChange={(e) => setVoiceQuestion(e.target.value)}
                />
                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => setShowVoiceInput(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleVoiceQuestion}
                    disabled={!voiceQuestion.trim()}
                    className="flex-1 bg-orange-600 hover:bg-orange-700"
                  >
                    Ask
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Rating Modal */}
        {showRating && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Rate Your Quest</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-center gap-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Button
                      key={star}
                      variant="ghost"
                      onClick={() => setRating(star)}
                      className="p-1"
                    >
                      <Star
                        className={`h-8 w-8 ${
                          star <= rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                        }`}
                      />
                    </Button>
                  ))}
                </div>
                
                <Textarea
                  placeholder="Any notes about your cooking adventure? (optional)"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
                
                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => setShowRating(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleCompleteSession}
                    className="flex-1 bg-green-600 hover:bg-green-700"
                  >
                    Complete Quest
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={handleFileSelect}
        />
      </div>
    </Layout>
  );
}

interface NutritionCardProps {
  nutrition: any;
}

function NutritionCard({ nutrition }: NutritionCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Nutrition Facts</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex justify-between">
          <span>Calories</span>
          <span className="font-medium">{Math.round(nutrition.calories || 0)}</span>
        </div>
        <div className="flex justify-between">
          <span>Protein</span>
          <span className="font-medium">{Math.round(nutrition.protein || 0)}g</span>
        </div>
        <div className="flex justify-between">
          <span>Carbs</span>
          <span className="font-medium">{Math.round(nutrition.carbs || 0)}g</span>
        </div>
        <div className="flex justify-between">
          <span>Fat</span>
          <span className="font-medium">{Math.round(nutrition.fat || 0)}g</span>
        </div>
      </CardContent>
    </Card>
  );
}

interface IngredientsListProps {
  ingredients: any[];
}

function IngredientsList({ ingredients }: IngredientsListProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Ingredients</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {ingredients.map((ingredient, index) => (
            <div key={index} className="flex justify-between items-center">
              <span>{ingredient.name}</span>
              <span className="text-sm text-gray-600">
                {ingredient.quantity} {ingredient.unit}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}