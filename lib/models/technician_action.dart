enum TechnicianAction {
  checkIn,
  checkOut,
  statusUpdate,
  billingSubmit,
}

extension TechnicianActionX on TechnicianAction {
  String get label {
    switch (this) {
      case TechnicianAction.checkIn:
        return 'check_in';
      case TechnicianAction.checkOut:
        return 'check_out';
      case TechnicianAction.statusUpdate:
        return 'status_update';
      case TechnicianAction.billingSubmit:
        return 'billing_submit';
    }
  }
}
