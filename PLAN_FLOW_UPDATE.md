# Plan Selection Flow - Multi-Step Process

## Overview
Completely redesigned the plan selection flow into a clean 3-step process with proper separation of concerns.

## New Flow

### Step 1: Select Plans (`/plans`)
**File**: `templates/choose_plans.html`

**Features**:
- Clean card-based layout showing all available plans
- Click to select/deselect plans (no pagination needed - all plans visible)
- Visual feedback with selected state (border highlight, badge)
- Plan images, pricing, and included items
- Progress indicator showing current step
- Selected count display
- Stores selections in sessionStorage
- Proceeds to customization page

**UI/UX Improvements**:
- Large, clear plan cards with hover effects
- Selected badge appears on chosen plans
- Fixed bottom bar shows selected count
- One-click selection (no checkboxes)
- Smooth animations and transitions

### Step 2: Customize Duration (`/plans/customize`)
**File**: `templates/customize_plans.html`

**Features**:
- Shows only selected plans from Step 1
- Quick duration options: 1 day, 3 days, 7 days, 30 days
- Custom date range option
- Real-time cost calculation per plan
- Order summary with total
- Validates date ranges
- Stores configurations in sessionStorage
- Proceeds to payment

**Duration Options**:
- **1 Day**: Quick trial
- **3 Days**: Short-term
- **7 Days**: Weekly
- **30 Days**: Monthly
- **Custom**: Pick your own start and end dates

**UI/UX Improvements**:
- Card per selected plan
- Visual selection of duration options
- Expandable custom date picker
- Live cost calculation
- Total summary at bottom
- Progress indicator

### Step 3: Payment (`/plans/checkout`)
**File**: `templates/plan_checkout.html`

**Features**:
- Stripe payment integration
- Order summary sidebar (sticky)
- Secure card input
- Payment processing
- Redirects to success/failure page

**UI/UX Improvements**:
- Two-column layout (form + summary)
- Sticky order summary
- Security badges
- Loading states
- Error handling

### Step 4: Success/Failure
**Files**: `templates/payment_success.html`, `templates/payment_failed.html`

**Features**:
- Success page shows transaction details
- Failure page allows retry
- Both already existed, now integrated into flow

## Backend Routes

### New Routes Added

1. **`GET /plans`** - Step 1: Select plans
   - Shows all active plans
   - Clean selection interface

2. **`GET /plans/customize`** - Step 2: Customize duration
   - Duration selection page
   - Uses sessionStorage data

3. **`GET /plans/checkout`** - Step 3: Payment
   - Checkout page with Stripe
   - Creates payment intent

4. **`POST /plans/process-payment`** - Process payment
   - Creates Stripe PaymentIntent
   - Stores pending configurations in session
   - Returns client secret

5. **`POST /plans/payment-success`** - Handle success
   - Verifies payment with Stripe
   - Creates CustomerPlan records
   - Activates subscriptions
   - Redirects to success page

### Old Route (Kept for compatibility)
- **`POST /plans/save`** - Direct save (old flow)

## Data Flow

```
Step 1 (Select Plans)
  ↓ sessionStorage: selectedPlans
Step 2 (Customize Duration)
  ↓ sessionStorage: planConfigurations
Step 3 (Checkout)
  ↓ session: pending_plan_configs
  ↓ Stripe PaymentIntent
Step 4 (Payment Success)
  ↓ Database: CustomerPlan records
  ↓ Redirect to success page
```

## Session Storage Structure

### selectedPlans
```javascript
[
  {
    id: 1,
    name: "Veg Thali",
    rate: "120"
  },
  ...
]
```

### planConfigurations
```javascript
{
  "1": {
    planId: 1,
    planName: "Veg Thali",
    dailyRate: 120,
    startDate: "2026-02-18",
    endDate: "2026-02-24",
    days: 7,
    totalCost: 840
  },
  ...
}
```

## Key Improvements

1. **Separation of Concerns**
   - Plan selection separate from duration
   - Duration separate from payment
   - Each step has clear purpose

2. **Better UX**
   - No overwhelming forms
   - Progressive disclosure
   - Clear progress indication
   - Visual feedback at each step

3. **Flexibility**
   - Quick duration presets (1, 3, 7, 30 days)
   - Custom date ranges
   - Multiple plan selection

4. **Payment Integration**
   - Proper Stripe integration
   - Secure payment flow
   - Success/failure handling

5. **Clean UI**
   - Modern card-based design
   - Consistent styling
   - Responsive layout
   - Smooth animations

## Testing Checklist

- [ ] Select single plan → customize → pay
- [ ] Select multiple plans → customize each → pay
- [ ] Use quick duration options (1, 3, 7, 30 days)
- [ ] Use custom date range
- [ ] Test payment success flow
- [ ] Test payment failure flow
- [ ] Verify CustomerPlan records created
- [ ] Check mobile responsiveness
- [ ] Test back navigation
- [ ] Verify session storage cleanup

## Files Modified

1. `templates/choose_plans.html` - Completely rewritten
2. `templates/customize_plans.html` - New file
3. `templates/plan_checkout.html` - New file
4. `app.py` - Added 5 new routes

## Files Used (Existing)

1. `templates/payment_success.html` - Already exists
2. `templates/payment_failed.html` - Already exists

## Next Steps

1. Test the complete flow
2. Add Stripe publishable key to `.env`
3. Test payment processing
4. Verify plan activation
5. Test edge cases (no selection, invalid dates, etc.)
