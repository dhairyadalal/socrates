/*
 * Proj:  MAGI - A System for Managing and Analyzing Genomic Information
 * Auth:  Huy Nguyen
 */
package com.myapp.magi.account.business;

import javax.ejb.Local;

import com.myapp.magi.exception.DataExistException;
import com.myapp.magi.account.model.User;
import com.myapp.magi.exception.FindSingleException;
import com.myapp.magi.exception.ValidationException;

/**
 * Manager of {@link User}. It provides methods for managing
 * a {@link User User}
 */
@Local
public interface AccountManager {

  public User findByLoginId(String id) throws FindSingleException;

  public void register(User u, Boolean validate)
      throws ValidationException, DataExistException;

  public void remove(User user);
}
