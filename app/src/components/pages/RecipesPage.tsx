import React, { useState, useEffect } from 'react';
import { Layout } from '../layout/Layout';
import { Search, Clock, Users, ChefHat, Sparkles, Play } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { recipeServiceGetRecipeRecommendations, recipeServiceGenerateRecipeFromIngredients, cookingServiceStartCookingSession } from '../../lib/sdk';
import type { BaseRecipe } from '../../lib/sdk';
import { useNavigate } from 'react-router-dom';

export function RecipesPage() {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCuisine, setSelectedCuisine] = useState<string>('');
  const [dietaryRestrictions, setDietaryRestrictions] = useState<string[]>([]);
  const navigate = useNavigate();

  // Temporary user ID - in real app this would come from auth
  const userId = "demo-user-1";

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      setIsLoading(true);
      const response = await recipeServiceGetRecipeRecommendations({
        body: { 
          user_id: userId,
          dietary_restrictions: dietaryRestrictions.length > 0 ? dietaryRestrictions : undefined
        }
      });
      if (response.data) {
        setRecommendations(response.data);
      }
    } catch (error) {
      console.error('Failed to load recipe recommendations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateRecipe = async () => {
    if (!searchQuery.trim()) return;

    try {
      setIsLoading(true);
      const ingredientList = searchQuery.split(',').map(s => s.trim()).filter(Boolean);
      
      const response = await recipeServiceGenerateRecipeFromIngredients({
        body: {
          ingredient_list: ingredientList,
          cuisine_preference: selectedCuisine || undefined,
          dietary_restrictions: dietaryRestrictions.length > 0 ? dietaryRestrictions : undefined
        }
      });
      
      if (response.data) {
        console.log('Generated recipe:', response.data);
        // In a real app, you'd show the generated recipe or add it to recommendations
        loadRecommendations(); // Refresh recommendations
      }
    } catch (error) {
      console.error('Failed to generate recipe:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartCooking = async (recipeId: string) => {
    try {
      const response = await cookingServiceStartCookingSession({
        body: {
          user_id: userId,
          base_recipe_id: recipeId
        }
      });
      
      if (response.data?.id) {
        navigate(`/cooking/${response.data.id}`);
      }
    } catch (error) {
      console.error('Failed to start cooking session:', error);
    }
  };

  const cuisineTypes = ['Italian', 'Asian', 'Mexican', 'Indian', 'Mediterranean', 'American'];
  const dietaryOptions = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'low-carb'];

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-3xl font-bold text-gray-900">Recipe Discovery</h1>
          <p className="text-gray-600">Find recipes based on your pantry or generate new ones with AI</p>
        </div>

        {/* Recipe Generator */}
        <Card className="border-orange-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-orange-600" />
              AI Recipe Generator
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ingredients (comma-separated)
                </label>
                <Input
                  placeholder="tomatoes, basil, mozzarella..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cuisine Type
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                  value={selectedCuisine}
                  onChange={(e) => setSelectedCuisine(e.target.value)}
                >
                  <option value="">Any cuisine</option>
                  {cuisineTypes.map(cuisine => (
                    <option key={cuisine} value={cuisine}>{cuisine}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Dietary Restrictions
              </label>
              <div className="flex flex-wrap gap-2">
                {dietaryOptions.map(option => (
                  <Badge
                    key={option}
                    variant={dietaryRestrictions.includes(option) ? "default" : "outline"}
                    className="cursor-pointer"
                    onClick={() => {
                      setDietaryRestrictions(prev =>
                        prev.includes(option)
                          ? prev.filter(d => d !== option)
                          : [...prev, option]
                      );
                    }}
                  >
                    {option}
                  </Badge>
                ))}
              </div>
            </div>
            
            <Button
              onClick={handleGenerateRecipe}
              disabled={isLoading || !searchQuery.trim()}
              className="bg-orange-600 hover:bg-orange-700"
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Generate Recipe
            </Button>
          </CardContent>
        </Card>

        {/* Recommendations */}
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Recommended for You</h2>
            <Button variant="outline" onClick={loadRecommendations}>
              Refresh
            </Button>
          </div>

          {isLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
              <p className="text-gray-600 mt-2">Loading recipes...</p>
            </div>
          ) : recommendations.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recommendations.map((rec, index) => (
                <RecipeCard
                  key={rec.recipe?.id || index}
                  recipe={rec.recipe}
                  matchPercentage={rec.match_percentage}
                  missingIngredients={rec.missing_ingredients}
                  onStartCooking={() => rec.recipe?.id && handleStartCooking(rec.recipe.id)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

interface RecipeCardProps {
  recipe: BaseRecipe;
  matchPercentage: number;
  missingIngredients: string[];
  onStartCooking: () => void;
}

function RecipeCard({ recipe, matchPercentage, missingIngredients, onStartCooking }: RecipeCardProps) {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start mb-2">
          <CardTitle className="text-lg leading-tight">{recipe.name}</CardTitle>
          <Badge className={`${matchPercentage >= 80 ? 'bg-green-100 text-green-800' : matchPercentage >= 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
            {Math.round(matchPercentage)}% match
          </Badge>
        </div>
        <p className="text-sm text-gray-600 line-clamp-2">{recipe.description}</p>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-1">
            <Clock className="h-4 w-4" />
            <span>{recipe.prep_time_minutes + recipe.cook_time_minutes}m</span>
          </div>
          <div className="flex items-center gap-1">
            <Users className="h-4 w-4" />
            <span>{recipe.servings}</span>
          </div>
          <Badge className={getDifficultyColor(recipe.difficulty_level)}>
            {recipe.difficulty_level}
          </Badge>
        </div>

        <div className="space-y-2">
          <div className="flex items-center gap-1">
            <ChefHat className="h-4 w-4 text-orange-600" />
            <span className="text-sm font-medium">{recipe.cuisine_type}</span>
          </div>
          
          {recipe.dietary_tags && recipe.dietary_tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {recipe.dietary_tags.map((tag, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          )}
        </div>

        {missingIngredients.length > 0 && (
          <div className="bg-orange-50 p-3 rounded-md">
            <p className="text-sm font-medium text-orange-800 mb-1">Missing ingredients:</p>
            <p className="text-xs text-orange-700">
              {missingIngredients.slice(0, 3).join(', ')}
              {missingIngredients.length > 3 && ` and ${missingIngredients.length - 3} more...`}
            </p>
          </div>
        )}

        <Button
          onClick={onStartCooking}
          className="w-full bg-orange-600 hover:bg-orange-700"
        >
          <Play className="h-4 w-4 mr-2" />
          Start Cooking Quest
        </Button>
      </CardContent>
    </Card>
  );
}

function EmptyState() {
  return (
    <div className="text-center py-12">
      <ChefHat className="h-16 w-16 text-gray-400 mx-auto mb-4" />
      <h3 className="text-xl font-semibold text-gray-900 mb-2">No recipes found</h3>
      <p className="text-gray-600 mb-6">
        Try scanning your pantry first or generate a recipe with specific ingredients
      </p>
      <Button className="bg-orange-600 hover:bg-orange-700">
        <Sparkles className="h-4 w-4 mr-2" />
        Generate Recipe
      </Button>
    </div>
  );
}