/*
 * Proj:  MAGI - A System for Managing and Analyzing Genomic Information
 * Auth:  Huy Nguyen
 */
package com.myapp.magi.account.business;

import java.util.HashMap;
import java.util.Map;

import javax.ejb.EJB;
import javax.ejb.EJBException;
import javax.ejb.Stateless;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.myapp.magi.exception.DataExistException;
import com.myapp.magi.account.model.User;
import com.myapp.magi.exception.FindSingleException;
import com.myapp.magi.exception.ValidationException;

/**
 * Manager of {@link User}. It provides methods for managing
 * a {@link User}.
 * 
 */
@Stateless(name = "AccountManager")
public class AccountManagerBean implements AccountManager {
  private static final Logger log = LoggerFactory
      .getLogger(AccountManagerBean.class);

  @EJB private UserDAO userDao;

  public AccountManagerBean() {  }

  public User findByLoginId(String id) throws FindSingleException {
    User u = userDao.findByLoginId(id);
    u = userDao.findByLoginId(id);
    return u;
  }

  public void register(User u, Boolean validate)
      throws ValidationException, DataExistException {
    log.debug("register: {}", u);

    if (validate) {
      validateFields(u);

      // check if the user exists by loginId
      try {
        userDao.findByLoginId(u.getLoginId());
        throw new DataExistException("User exists: " + u.getLoginId());
      } catch (FindSingleException e) {
        // expected
      }
    }
    // TODO: catch SQL error to be informative
    try {
      userDao.persist(u);
    } catch (Exception e) {
      throw new EJBException(e);
    }
  }

  public void remove(User user) {
    userDao.remove(user);
  }

  public void validateFields(User u) throws ValidationException {
    Map<String, String> errors = new HashMap<String, String>();

    if (u.getLoginId() == null || u.getLoginId().length() > 15) {
      errors
          .put("loginId", "Login ID must be between 1 and 15 chars");
    }
    if (u.getFirstName() == null || u.getFirstName().length() > 15) {
      errors.put("firstName",
          "First Name must be between 1 and 15 chars");
    }
    if (u.getLastName() == null || u.getLastName().length() > 15) {
      errors.put("lastName",
          "Last Name must be between 1 and 15 chars");
    }
    if (errors.size() > 0) {
      throw new ValidationException("There are invalid fields",
          errors);
    }
  }
}
