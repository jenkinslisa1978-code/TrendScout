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
  Loader2,
  Search,
  Filter,
  MoreVertical,
  Shield,
  Sparkles
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

const MOCK_USERS = [
  { id: '1', email: 'john@example.com', full_name: 'John Smith', plan: 'pro', status: 'active', created_at: '2024-01-15' },
  { id: '2', email: 'sarah@example.com', full_name: 'Sarah Johnson', plan: 'elite', status: 'active', created_at: '2024-02-20' },
  { id: '3', email: 'mike@example.com', full_name: 'Mike Wilson', plan: 'starter', status: 'active', created_at: '2024-03-10' },
];

const MOCK_SUBSCRIPTIONS = [
  { id: '1', user_email: 'john@example.com', plan_name: 'pro', status: 'active', amount: '$49/mo', current_period_end: '2024-04-15' },
  { id: '2', user_email: 'sarah@example.com', plan_name: 'elite', amount: '$99/mo', status: 'active', current_period_end: '2024-05-20' },
  { id: '3', user_email: 'mike@example.com', plan_name: 'starter', amount: '$0/mo', status: 'active', current_period_end: '2024-03-25' },
];

export default function AdminPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState(INITIAL_PRODUCT);
  const [saving, setSaving] = useState(false);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

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
      toast.success(editingProduct ? 'Product updated successfully' : 'Product created successfully');
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
      toast.success('Product deleted successfully');
      setDeleteConfirmId(null);
      fetchProducts();
    }
  };

  const filteredProducts = products.filter(p => 
    p.product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Premium Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 shadow-lg">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="font-manrope text-3xl font-extrabold text-slate-900 tracking-tight">Admin Panel</h1>
                <p className="text-slate-500">Manage products, users, and subscriptions</p>
              </div>
            </div>
          </div>
        </div>

        {/* Premium Tabs */}
        <Tabs defaultValue="products" className="space-y-6">
          <div className="flex items-center justify-between">
            <TabsList className="bg-slate-100/80 p-1.5 rounded-xl">
              <TabsTrigger 
                value="products" 
                className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg px-5 py-2.5 font-semibold" 
                data-testid="tab-products"
              >
                <Package className="mr-2 h-4 w-4" />
                Products
              </TabsTrigger>
              <TabsTrigger 
                value="users" 
                className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg px-5 py-2.5 font-semibold" 
                data-testid="tab-users"
              >
                <Users className="mr-2 h-4 w-4" />
                Users
              </TabsTrigger>
              <TabsTrigger 
                value="subscriptions" 
                className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg px-5 py-2.5 font-semibold" 
                data-testid="tab-subscriptions"
              >
                <CreditCard className="mr-2 h-4 w-4" />
                Subscriptions
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Products Tab */}
          <TabsContent value="products">
            <Card className="border-0 shadow-card overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-slate-50 to-white border-b border-slate-100 py-5">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="font-manrope text-xl font-bold text-slate-900">
                      Products Database
                    </CardTitle>
                    <p className="text-sm text-slate-500 mt-1">{products.length} products tracked</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <Input
                        placeholder="Search products..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10 w-64 h-10 bg-white"
                      />
                    </div>
                    <Button 
                      onClick={handleOpenCreate}
                      className="bg-indigo-600 hover:bg-indigo-700 shadow-md font-semibold h-10"
                      data-testid="add-product-btn"
                    >
                      <Plus className="mr-2 h-4 w-4" />
                      Add Product
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                {loading ? (
                  <div className="flex items-center justify-center py-16">
                    <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table className="table-premium">
                      <TableHeader>
                        <TableRow className="bg-slate-50/80 hover:bg-slate-50/80">
                          <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider py-4">Product</TableHead>
                          <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider">Category</TableHead>
                          <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider text-center">Score</TableHead>
                          <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider">Stage</TableHead>
                          <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider">Opportunity</TableHead>
                          <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider text-right">Margin</TableHead>
                          <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredProducts.map((product) => (
                          <TableRow key={product.id} className="hover:bg-slate-50/50" data-testid={`product-row-${product.id}`}>
                            <TableCell className="py-4">
                              <div className="flex items-center gap-3">
                                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50">
                                  <Package className="h-5 w-5 text-indigo-500" />
                                </div>
                                <div>
                                  <p className="font-semibold text-slate-900">{product.product_name}</p>
                                  {product.is_premium && (
                                    <Badge className="mt-1 bg-amber-100 text-amber-700 border-0 text-[10px] uppercase">
                                      <Sparkles className="h-2.5 w-2.5 mr-1" />
                                      Premium
                                    </Badge>
                                  )}
                                </div>
                              </div>
                            </TableCell>
                            <TableCell className="text-slate-600">{product.category}</TableCell>
                            <TableCell className="text-center">
                              <span className="font-mono text-lg font-bold text-slate-900">{product.trend_score}</span>
                            </TableCell>
                            <TableCell>
                              <Badge className={`${getTrendStageColor(product.trend_stage)} border text-xs font-semibold uppercase`}>
                                {product.trend_stage}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Badge className={`${getOpportunityColor(product.opportunity_rating)} border text-xs font-semibold uppercase`}>
                                {product.opportunity_rating}
                              </Badge>
                            </TableCell>
                            <TableCell className="text-right font-mono font-semibold text-emerald-600">
                              {formatCurrency(product.estimated_margin)}
                            </TableCell>
                            <TableCell className="text-right">
                              <div className="flex items-center justify-end gap-1">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => handleOpenEdit(product)}
                                  className="h-9 w-9 rounded-lg hover:bg-slate-100"
                                  data-testid={`edit-btn-${product.id}`}
                                >
                                  <Pencil className="h-4 w-4 text-slate-500" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-9 w-9 rounded-lg text-red-500 hover:text-red-600 hover:bg-red-50"
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
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users">
            <Card className="border-0 shadow-card overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-slate-50 to-white border-b border-slate-100 py-5">
                <div>
                  <CardTitle className="font-manrope text-xl font-bold text-slate-900">
                    User Management
                  </CardTitle>
                  <p className="text-sm text-slate-500 mt-1">{MOCK_USERS.length} registered users</p>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <Table className="table-premium">
                  <TableHeader>
                    <TableRow className="bg-slate-50/80 hover:bg-slate-50/80">
                      <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider py-4">User</TableHead>
                      <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider">Email</TableHead>
                      <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider">Plan</TableHead>
                      <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider">Status</TableHead>
                      <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider">Joined</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {MOCK_USERS.map((user) => (
                      <TableRow key={user.id} className="hover:bg-slate-50/50">
                        <TableCell className="py-4">
                          <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 text-white font-bold text-sm">
                              {user.full_name.split(' ').map(n => n[0]).join('')}
                            </div>
                            <span className="font-semibold text-slate-900">{user.full_name}</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-slate-600">{user.email}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className={`capitalize font-semibold ${
                            user.plan === 'elite' ? 'border-purple-200 bg-purple-50 text-purple-700' :
                            user.plan === 'pro' ? 'border-indigo-200 bg-indigo-50 text-indigo-700' :
                            'border-slate-200 bg-slate-50 text-slate-700'
                          }`}>
                            {user.plan}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className="bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
                            {user.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-slate-500 font-mono text-sm">{user.created_at}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Subscriptions Tab */}
          <TabsContent value="subscriptions">
            <Card className="border-0 shadow-card overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-slate-50 to-white border-b border-slate-100 py-5">
                <div>
                  <CardTitle className="font-manrope text-xl font-bold text-slate-900">
                    Subscriptions
                  </CardTitle>
                  <p className="text-sm text-slate-500 mt-1">{MOCK_SUBSCRIPTIONS.length} active subscriptions</p>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <Table className="table-premium">
                  <TableHeader>
                    <TableRow className="bg-slate-50/80 hover:bg-slate-50/80">
                      <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider py-4">User</TableHead>
                      <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider">Plan</TableHead>
                      <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider">Amount</TableHead>
                      <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider">Status</TableHead>
                      <TableHead className="font-bold text-slate-600 uppercase text-xs tracking-wider">Renews</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {MOCK_SUBSCRIPTIONS.map((sub) => (
                      <TableRow key={sub.id} className="hover:bg-slate-50/50">
                        <TableCell className="py-4 font-semibold text-slate-900">{sub.user_email}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className={`capitalize font-semibold ${
                            sub.plan_name === 'elite' ? 'border-purple-200 bg-purple-50 text-purple-700' :
                            sub.plan_name === 'pro' ? 'border-indigo-200 bg-indigo-50 text-indigo-700' :
                            'border-slate-200 bg-slate-50 text-slate-700'
                          }`}>
                            {sub.plan_name}
                          </Badge>
                        </TableCell>
                        <TableCell className="font-mono font-semibold text-slate-900">{sub.amount}</TableCell>
                        <TableCell>
                          <Badge className="bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
                            {sub.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-slate-500 font-mono text-sm">{sub.current_period_end}</TableCell>
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
            <DialogHeader className="pb-4 border-b border-slate-100">
              <DialogTitle className="font-manrope text-2xl font-bold">
                {editingProduct ? 'Edit Product' : 'Add New Product'}
              </DialogTitle>
            </DialogHeader>

            <div className="grid grid-cols-2 gap-5 py-6">
              <div className="col-span-2 space-y-2">
                <Label htmlFor="product_name" className="font-semibold">Product Name *</Label>
                <Input
                  id="product_name"
                  value={formData.product_name}
                  onChange={(e) => setFormData({ ...formData, product_name: e.target.value })}
                  placeholder="Portable Neck Fan"
                  className="h-11"
                  data-testid="input-product-name"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category" className="font-semibold">Category *</Label>
                <Input
                  id="category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  placeholder="Electronics"
                  className="h-11"
                  data-testid="input-category"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="trend_score" className="font-semibold">Trend Score (0-100) *</Label>
                <Input
                  id="trend_score"
                  type="number"
                  min="0"
                  max="100"
                  value={formData.trend_score}
                  onChange={(e) => setFormData({ ...formData, trend_score: e.target.value })}
                  placeholder="85"
                  className="h-11"
                  data-testid="input-trend-score"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="supplier_cost" className="font-semibold">Supplier Cost (£) *</Label>
                <Input
                  id="supplier_cost"
                  type="number"
                  step="0.01"
                  value={formData.supplier_cost}
                  onChange={(e) => setFormData({ ...formData, supplier_cost: e.target.value })}
                  placeholder="8.50"
                  className="h-11"
                  data-testid="input-supplier-cost"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="estimated_retail_price" className="font-semibold">Retail Price (£) *</Label>
                <Input
                  id="estimated_retail_price"
                  type="number"
                  step="0.01"
                  value={formData.estimated_retail_price}
                  onChange={(e) => setFormData({ ...formData, estimated_retail_price: e.target.value })}
                  placeholder="29.99"
                  className="h-11"
                  data-testid="input-retail-price"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="tiktok_views" className="font-semibold">TikTok Views</Label>
                <Input
                  id="tiktok_views"
                  type="number"
                  value={formData.tiktok_views}
                  onChange={(e) => setFormData({ ...formData, tiktok_views: e.target.value })}
                  placeholder="15000000"
                  className="h-11"
                  data-testid="input-tiktok-views"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="ad_count" className="font-semibold">Ad Count</Label>
                <Input
                  id="ad_count"
                  type="number"
                  value={formData.ad_count}
                  onChange={(e) => setFormData({ ...formData, ad_count: e.target.value })}
                  placeholder="234"
                  className="h-11"
                  data-testid="input-ad-count"
                />
              </div>

              <div className="space-y-2">
                <Label className="font-semibold">Trend Stage</Label>
                <Select 
                  value={formData.trend_stage} 
                  onValueChange={(v) => setFormData({ ...formData, trend_stage: v })}
                >
                  <SelectTrigger className="h-11" data-testid="select-trend-stage">
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
                <Label className="font-semibold">Competition Level</Label>
                <Select 
                  value={formData.competition_level} 
                  onValueChange={(v) => setFormData({ ...formData, competition_level: v })}
                >
                  <SelectTrigger className="h-11" data-testid="select-competition">
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
                <Label className="font-semibold">Opportunity Rating</Label>
                <Select 
                  value={formData.opportunity_rating} 
                  onValueChange={(v) => setFormData({ ...formData, opportunity_rating: v })}
                >
                  <SelectTrigger className="h-11" data-testid="select-opportunity">
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
                <Label htmlFor="short_description" className="font-semibold">Short Description</Label>
                <Input
                  id="short_description"
                  value={formData.short_description}
                  onChange={(e) => setFormData({ ...formData, short_description: e.target.value })}
                  placeholder="Brief product description"
                  className="h-11"
                  data-testid="input-description"
                />
              </div>

              <div className="col-span-2 space-y-2">
                <Label htmlFor="ai_summary" className="font-semibold">AI Analysis Summary</Label>
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
                <Label htmlFor="supplier_link" className="font-semibold">Supplier Link</Label>
                <Input
                  id="supplier_link"
                  value={formData.supplier_link}
                  onChange={(e) => setFormData({ ...formData, supplier_link: e.target.value })}
                  placeholder="https://alibaba.com/..."
                  className="h-11"
                  data-testid="input-supplier-link"
                />
              </div>

              <div className="col-span-2 flex items-center gap-3 p-4 bg-slate-50 rounded-xl">
                <input
                  type="checkbox"
                  id="is_premium"
                  checked={formData.is_premium}
                  onChange={(e) => setFormData({ ...formData, is_premium: e.target.checked })}
                  className="h-5 w-5 rounded border-slate-300"
                  data-testid="input-is-premium"
                />
                <Label htmlFor="is_premium" className="font-semibold cursor-pointer">
                  Premium Product (Pro/Elite only)
                </Label>
              </div>
            </div>

            <DialogFooter className="pt-4 border-t border-slate-100">
              <Button variant="outline" onClick={() => setDialogOpen(false)} className="h-11">
                Cancel
              </Button>
              <Button 
                onClick={handleSave}
                disabled={saving}
                className="bg-indigo-600 hover:bg-indigo-700 h-11 px-6 font-semibold"
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
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle className="font-manrope text-xl font-bold">Delete Product</DialogTitle>
            </DialogHeader>
            <p className="text-slate-600 py-4">
              Are you sure you want to delete this product? This action cannot be undone.
            </p>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDeleteConfirmId(null)}>
                Cancel
              </Button>
              <Button 
                variant="destructive" 
                onClick={() => handleDelete(deleteConfirmId)}
                className="bg-red-600 hover:bg-red-700"
                data-testid="confirm-delete-btn"
              >
                Delete Product
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
