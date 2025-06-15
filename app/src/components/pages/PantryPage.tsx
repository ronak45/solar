import { Camera, Plus, Search, Package, Trash2, Pencil } from "lucide-react";
import React, { useState, useEffect, useRef } from 'react';
import { Layout } from '../layout/Layout';

import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { pantryServiceScanPantryItems, pantryServiceGetUserPantry, pantryServiceAddPantryItem, pantryServiceSearchPantryItems, pantryServiceRemovePantryItem } from '../../lib/sdk';
import type { PantryItem } from '../../lib/sdk';

export function PantryPage() {
  const [pantryItems, setPantryItems] = useState<PantryItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showScanner, setShowScanner] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Temporary user ID - in real app this would come from auth
  const userId = "demo-user-1";

  useEffect(() => {
    loadPantryItems();
  }, []);

  const loadPantryItems = async () => {
    try {
      setIsLoading(true);
      const response = await pantryServiceGetUserPantry({
        body: { user_id: userId }
      });
      if (response.data) {
        setPantryItems(response.data);
      }
    } catch (error) {
      console.error('Failed to load pantry items:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageScan = async (file: File) => {
    try {
      setIsLoading(true);
      const response = await pantryServiceScanPantryItems({
        body: { image: file, user_id: userId }
      });
      
      if (response.data) {
        // Show scanned items for confirmation
        console.log('Scanned items:', response.data);
        // In a real app, you'd show a confirmation dialog here
        loadPantryItems(); // Refresh the list
      }
    } catch (error) {
      console.error('Failed to scan pantry items:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleImageScan(file);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadPantryItems();
      return;
    }

    try {
      setIsLoading(true);
      const response = await pantryServiceSearchPantryItems({
        body: { user_id: userId, query: searchQuery }
      });
      if (response.data) {
        setPantryItems(response.data);
      }
    } catch (error) {
      console.error('Failed to search pantry items:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveItem = async (itemId: string) => {
    try {
      await pantryServiceRemovePantryItem({
        body: { item_id: itemId }
      });
      loadPantryItems(); // Refresh the list
    } catch (error) {
      console.error('Failed to remove pantry item:', error);
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      vegetables: 'bg-green-100 text-green-800',
      fruits: 'bg-red-100 text-red-800',
      proteins: 'bg-blue-100 text-blue-800',
      grains: 'bg-yellow-100 text-yellow-800',
      dairy: 'bg-purple-100 text-purple-800',
      spices: 'bg-orange-100 text-orange-800',
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Pantry</h1>
            <p className="text-gray-600">Manage your ingredient inventory</p>
          </div>
          
          <div className="flex gap-3">
            <Button
              onClick={() => fileInputRef.current?.click()}
              className="bg-orange-600 hover:bg-orange-700"
              disabled={isLoading}
            >
              <Camera className="h-4 w-4 mr-2" />
              Scan Items
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowAddForm(true)}
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Item
            </Button>
          </div>
        </div>

        {/* Search */}
        <div className="flex gap-3">
          <div className="flex-1">
            <Input
              placeholder="Search pantry items..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <Button onClick={handleSearch} variant="outline">
            <Search className="h-4 w-4" />
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatsCard
            title="Total Items"
            value={pantryItems.length.toString()}
            icon={<Package className="h-5 w-5" />}
          />
          <StatsCard
            title="Categories"
            value={new Set(pantryItems.map(item => item.category)).size.toString()}
            icon={<Package className="h-5 w-5" />}
          />
          <StatsCard
            title="Low Stock"
            value={pantryItems.filter(item => item.quantity < 1).length.toString()}
            icon={<Package className="h-5 w-5" />}
          />
          <StatsCard
            title="Expiring Soon"
            value="0" // Would need date logic
            icon={<Package className="h-5 w-5" />}
          />
        </div>

        {/* Pantry Items Grid */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
            <p className="text-gray-600 mt-2">Loading pantry items...</p>
          </div>
        ) : pantryItems.length === 0 ? (
          <EmptyState onScanClick={() => fileInputRef.current?.click()} />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pantryItems.map((item) => (
              <PantryItemCard
                key={item.id}
                item={item}
                onRemove={() => item.id && handleRemoveItem(item.id)}
              />
            ))}
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

interface StatsCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
}

function StatsCard({ title, value, icon }: StatsCardProps) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center space-x-3">
          <div className="text-orange-600">{icon}</div>
          <div>
            <p className="text-sm text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

interface PantryItemCardProps {
  item: PantryItem;
  onRemove: () => void;
}

function PantryItemCard({ item, onRemove }: PantryItemCardProps) {
  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      vegetables: 'bg-green-100 text-green-800',
      fruits: 'bg-red-100 text-red-800',
      proteins: 'bg-blue-100 text-blue-800',
      grains: 'bg-yellow-100 text-yellow-800',
      dairy: 'bg-purple-100 text-purple-800',
      spices: 'bg-orange-100 text-orange-800',
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg">{item.name}</CardTitle>
            {item.brand && (
              <p className="text-sm text-gray-600">{item.brand}</p>
            )}
          </div>
          <div className="flex gap-1">
            <Button size="sm" variant="ghost">
              <Pencil className="h-4 w-4" />
            </Button>
            <Button size="sm" variant="ghost" onClick={onRemove}>
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-lg font-semibold">
              {item.quantity} {item.unit}
            </span>
            <Badge className={getCategoryColor(item.category)}>
              {item.category}
            </Badge>
          </div>
          
          {item.tags && item.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {item.tags.map((tag, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          )}
          
          {item.image_path && (
            <div className="w-full h-32 bg-gray-100 rounded-md overflow-hidden">
              <img
                src={item.image_path}
                alt={item.name}
                className="w-full h-full object-cover"
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

interface EmptyStateProps {
  onScanClick: () => void;
}

function EmptyState({ onScanClick }: EmptyStateProps) {
  return (
    <div className="text-center py-12">
      <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
      <h3 className="text-xl font-semibold text-gray-900 mb-2">Your pantry is empty</h3>
      <p className="text-gray-600 mb-6">
        Start by scanning your pantry items or adding ingredients manually
      </p>
      <div className="flex justify-center gap-3">
        <Button onClick={onScanClick} className="bg-orange-600 hover:bg-orange-700">
          <Camera className="h-4 w-4 mr-2" />
          Scan Items
        </Button>
        <Button variant="outline">
          <Plus className="h-4 w-4 mr-2" />
          Add Manually
        </Button>
      </div>
    </div>
  );
}