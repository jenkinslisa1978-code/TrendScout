import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Plus, 
  Pencil, 
  Trash2, 
  Package,
  Users,
  CreditCard,
  Loader2
} from 'lucide-react';
import { getProducts, createProduct, updateProduct, deleteProduct } from '@/services/productService';
import { formatCurrency, getTrendStageColor, getOpportunityColor } from '@/lib/utils';
import { toast } from 'sonner';

const INITIAL_PRODUCT = {
  product_name: '',
  category: '',
  short_description: '',
  supplier_cost: '',
  estimated_retail_price: '',
  tiktok_views: '',
  ad_count: '',
  competition_level: 'medium',
  trend_score: '',
  trend_stage: 'rising',
  opportunity_rating: 'medium',
  ai_summary: '',
  supplier_link: '',
  is_premium: false
};

// Mock users for demo
const MOCK_USERS = [
  { id: '1', email: 'john@example.com', full_name: 'John Smith', plan: 'pro', created_at: '2024-01-15' },
  { id: '2', email: 'sarah@example.com', full_name: 'Sarah Johnson', plan: 'elite', created_at: '2024-02-20' },
  { id: '3', email: 'mike@example.com', full_name: 'Mike Wilson', plan: 'starter', created_at: '2024-03-10' },
];

// Mock subscriptions for demo
const MOCK_SUBSCRIPTIONS = [
  { id: '1', user_email: 'john@example.com', plan_name: 'pro', status: 'active', current_period_end: '2024-04-15' },
  { id: '2', user_email: 'sarah@example.com', plan_name: 'elite', status: 'active', current_period_end: '2024-05-20' },
  { id: '3', user_email: 'mike@example.com', plan_name: 'starter', status: 'active', current_period_end: '2024-03-25' },
];

export default function AdminPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState(INITIAL_PRODUCT);
  const [saving, setSaving] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    setLoading(true);
    const { data } = await getProducts({});
    if (data) setProducts(data);
    setLoading(false);
  };

  const handleOpenCreate = () => {
    setEditingProduct(null);
    setFormData(INITIAL_PRODUCT);
    setDialogOpen(true);
  };

  const handleOpenEdit = (product) => {
    setEditingProduct(product);
    setFormData({
      product_name: product.product_name,
      category: product.category,
      short_description: product.short_description || '',
      supplier_cost: product.supplier_cost.toString(),
      estimated_retail_price: product.estimated_retail_price.toString(),
      tiktok_views: product.tiktok_views.toString(),
      ad_count: product.ad_count.toString(),
      competition_level: product.competition_level,
      trend_score: product.trend_score.toString(),
      trend_stage: product.trend_stage,
      opportunity_rating: product.opportunity_rating,
      ai_summary: product.ai_summary || '',
      supplier_link: product.supplier_link || '',
      is_premium: product.is_premium
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    // Validation
    if (!formData.product_name || !formData.category || !formData.supplier_cost || 
        !formData.estimated_retail_price || !formData.trend_score) {
      toast.error('Please fill in all required fields');
      return;
    }

    setSaving(true);

    const productData = {
      product_name: formData.product_name,
      category: formData.category,
      short_description: formData.short_description,
      supplier_cost: parseFloat(formData.supplier_cost),
      estimated_retail_price: parseFloat(formData.estimated_retail_price),
      tiktok_views: parseInt(formData.tiktok_views) || 0,
      ad_count: parseInt(formData.ad_count) || 0,
      competition_level: formData.competition_level,
      trend_score: parseInt(formData.trend_score),
      trend_stage: formData.trend_stage,
      opportunity_rating: formData.opportunity_rating,
      ai_summary: formData.ai_summary,
      supplier_link: formData.supplier_link,
      is_premium: formData.is_premium
    };

    let result;
    if (editingProduct) {
      result = await updateProduct(editingProduct.id, productData);
    } else {
      result = await createProduct(productData);
    }

    if (result.error) {
      toast.error('Failed to save product');
    } else {
      toast.success(editingProduct ? 'Product updated' : 'Product created');
      setDialogOpen(false);
      fetchProducts();
    }

    setSaving(false);
  };

  const handleDelete = async (id) => {
    const { error } = await deleteProduct(id);
    
    if (error) {
      toast.error('Failed to delete product');
    } else {
      toast.success('Product deleted');
      setDeleteConfirmId(null);
      fetchProducts();
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="font-manrope text-2xl font-bold text-slate-900">Admin Panel</h1>
          <p className="mt-1 text-slate-500">Manage products, users, and subscriptions</p>
        </div>

        <Tabs defaultValue="products" className="space-y-6">
          <TabsList className="bg-slate-100">
            <TabsTrigger value="products" className="data-[state=active]:bg-white" data-testid="tab-products">
              <Package className="mr-2 h-4 w-4" />
              Products
            </TabsTrigger>
            <TabsTrigger value="users" className="data-[state=active]:bg-white" data-testid="tab-users">
              <Users className="mr-2 h-4 w-4" />
              Users
            </TabsTrigger>
            <TabsTrigger value="subscriptions" className="data-[state=active]:bg-white" data-testid="tab-subscriptions">
              <CreditCard className="mr-2 h-4 w-4" />
              Subscriptions
            </TabsTrigger>
          </TabsList>

          {/* Products Tab */}
          <TabsContent value="products">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="border-b border-slate-100">
                <div className="flex items-center justify-between">
                  <CardTitle className="font-manrope text-lg font-semibold text-slate-900">
                    Products ({products.length})
                  </CardTitle>
                  <Button 
                    onClick={handleOpenCreate}
                    className="bg-indigo-600 hover:bg-indigo-700"
                    data-testid="add-product-btn"
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    Add Product
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                {loading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-slate-50">
                        <TableHead>Product</TableHead>
                        <TableHead>Category</TableHead>
                        <TableHead className="text-right">Trend Score</TableHead>
                        <TableHead>Stage</TableHead>
                        <TableHead>Opportunity</TableHead>
                        <TableHead className="text-right">Margin</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {products.map((product) => (
                        <TableRow key={product.id} data-testid={`product-row-${product.id}`}>
                          <TableCell className="font-medium">{product.product_name}</TableCell>
                          <TableCell>{product.category}</TableCell>
                          <TableCell className="text-right font-mono">{product.trend_score}</TableCell>
                          <TableCell>
                            <Badge className={`${getTrendStageColor(product.trend_stage)} border text-xs`}>
                              {product.trend_stage}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge className={`${getOpportunityColor(product.opportunity_rating)} border text-xs`}>
                              {product.opportunity_rating}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right font-mono">
                            {formatCurrency(product.estimated_margin)}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex items-center justify-end gap-2">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleOpenEdit(product)}
                                data-testid={`edit-btn-${product.id}`}
                              >
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="text-red-500 hover:text-red-600 hover:bg-red-50"
                                onClick={() => setDeleteConfirmId(product.id)}
                                data-testid={`delete-btn-${product.id}`}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="border-b border-slate-100">
                <CardTitle className="font-manrope text-lg font-semibold text-slate-900">
                  Users ({MOCK_USERS.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50">
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Plan</TableHead>
                      <TableHead>Joined</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {MOCK_USERS.map((user) => (
                      <TableRow key={user.id}>
                        <TableCell className="font-medium">{user.full_name}</TableCell>
                        <TableCell>{user.email}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="capitalize">{user.plan}</Badge>
                        </TableCell>
                        <TableCell className="text-slate-500">{user.created_at}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Subscriptions Tab */}
          <TabsContent value="subscriptions">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="border-b border-slate-100">
                <CardTitle className="font-manrope text-lg font-semibold text-slate-900">
                  Subscriptions ({MOCK_SUBSCRIPTIONS.length})
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50">
                      <TableHead>User</TableHead>
                      <TableHead>Plan</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Renews</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {MOCK_SUBSCRIPTIONS.map((sub) => (
                      <TableRow key={sub.id}>
                        <TableCell className="font-medium">{sub.user_email}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="capitalize">{sub.plan_name}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className="bg-emerald-50 text-emerald-700 border border-emerald-200">
                            {sub.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-slate-500">{sub.current_period_end}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Product Form Dialog */}
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="font-manrope text-xl font-bold">
                {editingProduct ? 'Edit Product' : 'Add New Product'}
              </DialogTitle>
            </DialogHeader>

            <div className="grid grid-cols-2 gap-4 py-4">
              <div className="col-span-2 space-y-2">
                <Label htmlFor="product_name">Product Name *</Label>
                <Input
                  id="product_name"
                  value={formData.product_name}
                  onChange={(e) => setFormData({ ...formData, product_name: e.target.value })}
                  placeholder="Portable Neck Fan"
                  data-testid="input-product-name"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <Input
                  id="category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  placeholder="Electronics"
                  data-testid="input-category"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="trend_score">Trend Score (0-100) *</Label>
                <Input
                  id="trend_score"
                  type="number"
                  min="0"
                  max="100"
                  value={formData.trend_score}
                  onChange={(e) => setFormData({ ...formData, trend_score: e.target.value })}
                  placeholder="85"
                  data-testid="input-trend-score"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="supplier_cost">Supplier Cost (£) *</Label>
                <Input
                  id="supplier_cost"
                  type="number"
                  step="0.01"
                  value={formData.supplier_cost}
                  onChange={(e) => setFormData({ ...formData, supplier_cost: e.target.value })}
                  placeholder="8.50"
                  data-testid="input-supplier-cost"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="estimated_retail_price">Retail Price (£) *</Label>
                <Input
                  id="estimated_retail_price"
                  type="number"
                  step="0.01"
                  value={formData.estimated_retail_price}
                  onChange={(e) => setFormData({ ...formData, estimated_retail_price: e.target.value })}
                  placeholder="29.99"
                  data-testid="input-retail-price"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="tiktok_views">TikTok Views</Label>
                <Input
                  id="tiktok_views"
                  type="number"
                  value={formData.tiktok_views}
                  onChange={(e) => setFormData({ ...formData, tiktok_views: e.target.value })}
                  placeholder="15000000"
                  data-testid="input-tiktok-views"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="ad_count">Ad Count</Label>
                <Input
                  id="ad_count"
                  type="number"
                  value={formData.ad_count}
                  onChange={(e) => setFormData({ ...formData, ad_count: e.target.value })}
                  placeholder="234"
                  data-testid="input-ad-count"
                />
              </div>

              <div className="space-y-2">
                <Label>Trend Stage</Label>
                <Select 
                  value={formData.trend_stage} 
                  onValueChange={(v) => setFormData({ ...formData, trend_stage: v })}
                >
                  <SelectTrigger data-testid="select-trend-stage">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="early">Early</SelectItem>
                    <SelectItem value="rising">Rising</SelectItem>
                    <SelectItem value="peak">Peak</SelectItem>
                    <SelectItem value="saturated">Saturated</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Competition Level</Label>
                <Select 
                  value={formData.competition_level} 
                  onValueChange={(v) => setFormData({ ...formData, competition_level: v })}
                >
                  <SelectTrigger data-testid="select-competition">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Opportunity Rating</Label>
                <Select 
                  value={formData.opportunity_rating} 
                  onValueChange={(v) => setFormData({ ...formData, opportunity_rating: v })}
                >
                  <SelectTrigger data-testid="select-opportunity">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="very high">Very High</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="col-span-2 space-y-2">
                <Label htmlFor="short_description">Short Description</Label>
                <Input
                  id="short_description"
                  value={formData.short_description}
                  onChange={(e) => setFormData({ ...formData, short_description: e.target.value })}
                  placeholder="Brief product description"
                  data-testid="input-description"
                />
              </div>

              <div className="col-span-2 space-y-2">
                <Label htmlFor="ai_summary">AI Analysis Summary</Label>
                <Textarea
                  id="ai_summary"
                  value={formData.ai_summary}
                  onChange={(e) => setFormData({ ...formData, ai_summary: e.target.value })}
                  placeholder="Detailed AI-generated market analysis..."
                  rows={3}
                  data-testid="input-ai-summary"
                />
              </div>

              <div className="col-span-2 space-y-2">
                <Label htmlFor="supplier_link">Supplier Link</Label>
                <Input
                  id="supplier_link"
                  value={formData.supplier_link}
                  onChange={(e) => setFormData({ ...formData, supplier_link: e.target.value })}
                  placeholder="https://alibaba.com/..."
                  data-testid="input-supplier-link"
                />
              </div>

              <div className="col-span-2 flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_premium"
                  checked={formData.is_premium}
                  onChange={(e) => setFormData({ ...formData, is_premium: e.target.checked })}
                  className="h-4 w-4 rounded border-slate-300"
                  data-testid="input-is-premium"
                />
                <Label htmlFor="is_premium">Premium Product (Pro/Elite only)</Label>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleSave}
                disabled={saving}
                className="bg-indigo-600 hover:bg-indigo-700"
                data-testid="save-product-btn"
              >
                {saving ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  editingProduct ? 'Update Product' : 'Create Product'
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog open={!!deleteConfirmId} onOpenChange={() => setDeleteConfirmId(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Product</DialogTitle>
            </DialogHeader>
            <p className="text-slate-600">
              Are you sure you want to delete this product? This action cannot be undone.
            </p>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDeleteConfirmId(null)}>
                Cancel
              </Button>
              <Button 
                variant="destructive" 
                onClick={() => handleDelete(deleteConfirmId)}
                data-testid="confirm-delete-btn"
              >
                Delete
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
